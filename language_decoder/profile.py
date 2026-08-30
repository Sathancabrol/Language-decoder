"""
Language-decoder — DecodedHuman profile (orchestrator + UI contract)
====================================================================

Ties the pipeline together:

    input (text / items / ai-json)
        -> decode        (Observations with alignment, channel, provenance)
        -> infer         (per-construct ConstructEstimate | Refusal)
        -> functioning   (ICF hypotheses)
        -> dynamics      (retention, transfer)
        -> profile       (DecodedHuman, the UI-facing contract)

The profile is what the interface consumes. It is JSON-safe, auditable, and
carries the epistemic and provenance guarantees of every layer above it. It
never emits a level-5 psychological conclusion.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .decoder import decode_text, decode_items, decode_ai_json, group_by_construct
from .dynamics import Retention, build_dynamics, transferability
from .evidence import Observation
from .functioning import project
from .inference import InferenceEngine, Refusal
from .ontology import DOMAIN_META, DOMAINS, BY_ID, Construct, constructs_by_domain

VERSION = "0.1.0"


@dataclass
class DomainBlock:
    domain: str
    title: str
    describe: str
    estimates: list = field(default_factory=list)
    refusals: list = field(default_factory=list)
    observations: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "domain": self.domain,
            "title": self.title,
            "describe": self.describe,
            "estimates": self.estimates,
            "refusals": self.refusals,
            "observations": self.observations,
        }


@dataclass
class DecodedHuman:
    id: str
    source_title: str
    created_at: str
    version: str = VERSION
    domains: dict = field(default_factory=dict)
    functioning: list = field(default_factory=list)
    dynamics: dict = field(default_factory=dict)
    refusals: list = field(default_factory=list)
    epistemic_summary: dict = field(default_factory=dict)
    ui_hints: dict = field(default_factory=dict)
    observations: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "source_title": self.source_title,
            "created_at": self.created_at,
            "version": self.version,
            "domains": {k: v.as_dict() for k, v in self.domains.items()},
            "functioning": self.functioning,
            "dynamics": self.dynamics,
            "refusals": self.refusals,
            "epistemic_summary": self.epistemic_summary,
            "ui_hints": self.ui_hints,
            "observations": self.observations,
            "notes": self.notes,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=indent)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def decode_human(
    text: str = "",
    *,
    items: list[dict] | None = None,
    ai_json: str = "",
    source_title: str = "Décodage humain",
    source_document: str = "narrative",
    person_id: str = "unknown",
    current_year: int = 2026,
    engine_options: dict | None = None,
    inits: dict | None = None,
) -> DecodedHuman:
    """
    Full decode pipeline. At least one of text/items/ai_json should be provided.

    `inits` may pre-seed Retention data for the dynamics block:
        {
          "retentions": [ {construct_id, base_level, last_practiced_year,
                           half_life_years, reactivated?} ]
          "transfer_bands": {construct_id: 0..1}
        }
    """
    observations: list[Observation] = []
    notes: list[str] = []

    if text.strip():
        observations += decode_text(text, source=source_document,
                                    source_document=source_document)
    if items:
        observations += decode_items(items, source_document=source_document)
    if ai_json:
        observations += decode_ai_json(ai_json, source_document=source_document)
        notes.append("Proposition(s) IA décodée(s) : niveau épistémique plafonné à 4 "
                     "(hypothèse à valider), jamais de conclusion psychologique.")

    if not observations:
        notes.append("Aucune observation décodée. Vérifiez que le texte contient "
                     "des marqueurs de construits identifiables.")
        return _empty_profile(person_id, source_title, source_document, current_year, notes)

    engine = InferenceEngine(engine_options)
    groups = group_by_construct(observations)

    domains: dict[str, DomainBlock] = {}
    all_refusals: list[dict] = []
    function_estimates: list[dict] = []

    for domain in DOMAINS:
        meta = DOMAIN_META[domain]
        block = DomainBlock(domain=domain, title=meta["title"], describe=meta["description"])
        for construct in constructs_by_domain(domain):
            group = groups.get(construct.id, [])
            if not group:
                continue
            result = engine.estimate(construct.id, group, epistemic_level=_default_epistemic(construct))
            if isinstance(result, Refusal):
                block.refusals.append(result.as_dict())
                all_refusals.append(result.as_dict())
            else:
                block.estimates.append(result.as_dict())
                function_estimates.append({
                    "construct_id": construct.id, "value": result.value,
                    "label": construct.label, "domain": result.domain,
                })
        # attach observations relevant to this domain
        block.observations = _observations_for_domain(observations, domain)
        domains[domain] = block

    functioning = [p.as_dict() for p in project(function_estimates)]

    dynamics = _build_dynamics_entry(inits or {}, current_year, groups, observations)

    refusals = [r for r in all_refusals]

    return DecodedHuman(
        id=person_id,
        source_title=source_title,
        created_at=datetime.now(timezone.utc).isoformat(),
        domains=domains,
        functioning=functioning,
        dynamics=dynamics,
        refusals=refusals,
        epistemic_summary=_epistemic_summary(domains, refusals),
        ui_hints=_ui_hints(domains, functioning, dynamics),
        observations=[o.as_dict() for o in observations],
        notes=notes,
    )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _default_epistemic(construct: Construct) -> int:
    """Map a construct's role/status to a baseline epistemic level (1-4)."""
    if construct.status == "ESTABLISHED":
        return 2
    if construct.status == "SUPPORTED":
        return 3
    return 3


def _observations_for_domain(observations: list[Observation], domain: str) -> list[dict]:
    domain_constructs = {c.id for c in constructs_by_domain(domain)}
    return [o.as_dict() for o in observations
            if any(cid in domain_constructs for cid in o.construct_ids)]


def _build_dynamics_entry(inits: dict, current_year: int, groups, observations) -> dict:
    retentions: list[Retention] = []
    for spec in inits.get("retentions", []):
        retentions.append(Retention(
            construct_id=spec["construct_id"],
            base_level=spec.get("base_level", 0.6),
            last_practiced_year=spec.get("last_practiced_year", current_year),
            half_life_years=spec.get("half_life_years", 4),
            current_year=current_year,
            reactivated=spec.get("reactivated", False),
        ))
    # If no explicit retention data, derive a soft one from any strong estimate.
    if not retentions:
        for cid, group in groups.items():
            strong = [o for o in group if o.confidence >= 0.6]
            if strong:
                c = BY_ID[cid]
                retentions.append(Retention(
                    construct_id=cid, base_level=max(0.4, strong[0].normalized_value or 0.5),
                    last_practiced_year=current_year, half_life_years=_default_half_life(c),
                    current_year=current_year,
                ))
    return build_dynamics(retentions, transfer_bands=inits.get("transfer_bands"),
                          current_year=current_year)


def _default_half_life(construct: Construct) -> float:
    # dispositional/capability constructs decay slowly; momentary modulators fast.
    if construct.domain == "action":
        return 6
    if construct.role == "state_modulator" or construct.typical_timescale in ("momentary", "daily"):
        return 2
    return 4


def _epistemic_summary(domains: dict, refusals: list[dict]) -> dict:
    total_est = sum(len(d.estimates) for d in domains.values())
    level_counts: dict[int, int] = {}
    for d in domains.values():
        for e in d.estimates:
            lvl = e.get("epistemic_level", 2)
            level_counts[lvl] = level_counts.get(lvl, 0) + 1
    return {
        "total_estimates": total_est,
        "total_refusals": len(refusals),
        "levels": level_counts,
        "max_level": max(level_counts) if level_counts else 0,
        "level5_present": False,  # guard: never auto
        "note": "Niveau 5 (conclusion psychologique) n'est jamais produit automatiquement.",
    }


def _ui_hints(domains: dict, functioning: list[dict], dynamics: dict) -> dict:
    """Lightweight hints so the UI can pick a representation per domain."""
    hints = {}
    for domain, block in domains.items():
        strengths = [e.get("value", 0) for e in block.estimates]
        avg = round(sum(strengths) / len(strengths), 3) if strengths else 0
        hints[domain] = {
            "estimate_count": len(block.estimates),
            "refusal_count": len(block.refusals),
            "average_value": avg,
            "representation": _representation_for_domain(domain),
            "top_strengths": sorted(
                [{ "label": e.get("construct_label"), "value": e.get("value"),
                   "strength": e.get("strength_label") } for e in block.estimates],
                key=lambda x: x["value"] or 0, reverse=True,
            )[:5],
        }
    if functioning:
        hints["functioning"] = {"representation": "list", "count": len(functioning)}
    if dynamics.get("retentions"):
        hints["dynamics"] = {"representation": "radar",
                             "count": len(dynamics["retentions"])}
    return hints


def _representation_for_domain(domain: str) -> str:
    if domain == "physical":
        return "cards"
    if domain == "mental":
        return "constellation"
    if domain == "action":
        return "radar"
    if domain == "dynamics":
        return "timeline"
    return "list"


def _empty_profile(person_id, source_title, source_document, current_year, notes) -> DecodedHuman:
    domains = {}
    for domain in DOMAINS:
        meta = DOMAIN_META[domain]
        domains[domain] = DomainBlock(domain=domain, title=meta["title"], describe=meta["description"])
    return DecodedHuman(
        id=person_id, source_title=source_title, created_at="",
        domains=domains,
        functioning=[], dynamics={"current_year": current_year, "retentions": [], "model": ""},
        refusals=[], epistemic_summary={"total_estimates": 0, "total_refusals": 0, "levels": {},
                                        "max_level": 0, "level5_present": False},
        ui_hints={}, observations=[], notes=notes,
    )
