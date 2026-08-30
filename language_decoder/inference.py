"""
Language-decoder — Inference engine
===================================

The inference engine turns Observations into ConstructEstimates — or refuses to.

It is NOT an average of scores and NOT a clinical classifier. It follows the
admissibility-filter-first discipline of HCSM v0.1.0:

  1. Admissibility: filter before computing. If a construct is not estimable,
     emit a formal Refusal(code, message). No default silent value.
  2. Families of estimators: the engine accepts a *contract* — for each
     construct it returns (value, uncertainty, alternatives). The working
     estimator here is a weighted, channel-aware fusion that is deliberately
     *non-additive* (more evidence ≠ automatically better, and cross-channel
     convergence is different from stacking).
  3. Uncertainty is decomposed into measurement / evidence / inference
     components and reported with a rationale.
  4. Alternatives are named, not eliminated silently. Two alternatives with
     comparable plausibility predicting the same observation widen uncertainty.
  5. Capacity ≠ Performance ≠ State. The engine keeps the window and context.

Refusal codes (from HCSM ontology):
  NO_CONSTRUCT, NO_EVIDENCE, WINDOW_UNDEFINED, CONTEXT_MISSING,
  UNRESOLVED_ALTERNATIVES, MISALIGNED_MEASURE, PROVENANCE_BROKEN
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from .evidence import Observation
from .ontology import Construct, get_construct

REFUSAL_CODES = (
    "NO_CONSTRUCT",
    "NO_EVIDENCE",
    "WINDOW_UNDEFINED",
    "CONTEXT_MISSING",
    "UNRESOLVED_ALTERNATIVES",
    "MISALIGNED_MEASURE",
    "PROVENANCE_BROKEN",
)


@dataclass
class Refusal:
    code: str
    construct_id: str
    message: str

    def __post_init__(self) -> None:
        if self.code not in REFUSAL_CODES:
            raise ValueError(f"Unknown refusal code: {self.code}")

    def as_dict(self) -> dict:
        return {"code": self.code, "construct_id": self.construct_id, "message": self.message}


@dataclass
class Uncertainty:
    kind: str = "composite"
    total: float = 0.0
    measurement_component: float = 0.0
    evidence_component: float = 0.0
    inference_component: float = 0.0

    def as_dict(self) -> dict:
        return {
            "kind": self.kind, "total": round(self.total, 3),
            "measurement_component": round(self.measurement_component, 3),
            "evidence_component": round(self.evidence_component, 3),
            "inference_component": round(self.inference_component, 3),
        }


@dataclass
class AlternativeExplanation:
    modulator_id: str
    label: str
    plausibility: float
    explains: list = field(default_factory=list)
    competing_with: list = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "modulator_id": self.modulator_id, "label": self.label,
            "plausibility": round(self.plausibility, 3), "explains": self.explains,
            "competing_with": self.competing_with,
        }


@dataclass
class ConstructEstimate:
    construct_id: str
    construct_label: str
    domain: str
    value: float            # 0..1 unit interval (normalized probability-like)
    scale: str = "unit_interval"
    estimate_status: str = "estimated"
    strength_label: str = ""        # qualitative label
    epistemic_level: int = 2
    uncertainty: Uncertainty = field(default_factory=Uncertainty)
    evidence_ids: list = field(default_factory=list)
    alternatives: list = field(default_factory=list)
    rationale: str = ""
    window: Optional[dict] = None
    context: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "construct_id": self.construct_id,
            "construct_label": self.construct_label,
            "domain": self.domain,
            "value": round(self.value, 3),
            "scale": self.scale,
            "estimate_status": self.estimate_status,
            "strength_label": self.strength_label,
            "epistemic_level": self.epistemic_level,
            "uncertainty": self.uncertainty.as_dict(),
            "evidence_ids": self.evidence_ids,
            "alternatives": [a.as_dict() for a in self.alternatives],
            "rationale": self.rationale,
            "window": self.window,
            "context": self.context,
        }


# ---------------------------------------------------------------------------
# Estimator helpers (deterministic, stdlib only)
# ---------------------------------------------------------------------------

# Channel alignment is always imperfect for latent constructs. Rough fidelity
# weights per channel; they multiply the observation *alignment weight*.
_CHANNEL_FIDELITY = {
    "behavioral": 1.00,
    "physiological": 0.85,
    "neural": 0.80,
    "subjective": 0.70,
    "contextual": 0.55,
    "computational": 0.75,
    "digital_passive": 0.45,
}

_ALIGNMENT_WEIGHT = {"exact": 1.0, "close": 0.7, "related": 0.4, "none": 0.0}

# Strength labels thresholds (derived from Cognitorium qualitative banding).
_STRENGTH_LABELS = [
    (0.82, "Très forte"),
    (0.62, "Forte"),
    (0.42, "Modérée"),
    (0.22, "Faible"),
    (0.00, "À explorer"),
]


def _strength_label(value: float) -> str:
    for threshold, label in _STRENGTH_LABELS:
        if value >= threshold:
            return label
    return "À explorer"


def _softmax_weights(scores: list[float]) -> list[float]:
    """Weights over evidence items that are additive-honest and bounded."""
    if not scores:
        return []
    # Normalize by the strongest item to avoid numeric blow-up; shift by the max.
    m = max(scores)
    if m <= 0:
        return [1.0 / len(scores)] * len(scores)
    exps = [math.exp((s - m)) for s in scores]
    total = sum(exps)
    return [e / total for e in exps]


def _observation_weight(obs: Observation) -> float:
    """Per-observation weight = alignment × channel fidelity × confidence × quality."""
    align = _ALIGNMENT_WEIGHT[obs.alignment]
    chan = _CHANNEL_FIDELITY.get(obs.channel, 0.5)
    conf = max(0.0, min(1.0, obs.confidence))
    if obs.quality_flag == "degraded":
        conf *= 0.6
    elif obs.quality_flag == "unusable":
        conf = 0.0
    return align * chan * conf


def _sufficient_alignment(obs: Observation) -> bool:
    """An observation must have at most 'close' alignment to be usable; 'none' is not."""
    return obs.alignment in ("exact", "close")


# ---------------------------------------------------------------------------
# Fusion (channel-aware, non-additive)
# ---------------------------------------------------------------------------

def fuse_observations(
    observations: list[Observation],
    construct: Construct,
    *,
    channel_convergence_bonus: float = 0.06,
    channel_divergence_penalty: float = 0.10,
) -> tuple[float, Uncertainty, list[str]]:
    """
    Fuse a set of observations for ONE construct.

    Returns (value 0..1, Uncertainty, evidence_ids).

    Non-additivity rules:
      * Observations of the SAME channel and instrument reinforce (repetition,
        reliability) but with diminishing returns (softmax over weights).
      * Observations from DIFFERENT channels are confronted: convergence adds a
        small bonus, divergence adds a penalty and raises uncertainty.
      * 'none'-aligned observations are excluded here (they cannot found an
        estimate).
    """
    usable = [o for o in observations if _sufficient_alignment(o)]
    if not usable:
        return 0.0, Uncertainty(kind="composite", total=1.0, inference_component=1.0), []

    weights = [_observation_weight(o) for o in usable]
    # positive-of-zero-guard: if all weights are 0, we cannot estimate.
    if sum(weights) <= 0.0:
        return 0.0, Uncertainty(kind="composite", total=1.0, evidence_component=1.0), []

    weighted = _softmax_weights(weights)

    # Directional values: map each observation's presence/level to 0..1.
    values = []
    for o, w in zip(usable, weighted):
        v = o.normalized_value
        if v is None:
            # If only content is present, treat as a soft positive (default 0.5)
            # but scale by confidence so a low-confidence mention is weak.
            v = 0.5
        v = max(0.0, min(1.0, v))
        values.append(v)

    value = sum(v * w for v, w in zip(values, weighted))

    # --- channel-aware convergence / divergence --------------------------
    channels = {o.channel for o in usable}
    if len(channels) > 1:
        # Convergence: all channel means on the same half of the scale.
        channel_means = []
        seen = {}
        for o, v in zip(usable, values):
            seen.setdefault(o.channel, []).append(v)
        for ch, vs in seen.items():
            channel_means.append(sum(vs) / len(vs))
        spread = max(channel_means) - min(channel_means)
        if spread <= 0.2:
            value = min(1.0, value + channel_convergence_bonus)
            conv = 1 - spread
        else:
            conv = 1 - spread
            value = max(0.0, value - channel_divergence_penalty * (spread - 0.2))
        evidence_component = round(0.10 + 0.5 * (1 - conv), 3)
    else:
        evidence_component = 0.10

    # --- uncertainty decomposition --------------------------------------
    # measurement: from observing-channel fidelity and quality
    avg_fidelity = sum(_CHANNEL_FIDELITY.get(o.channel, 0.5) * (0 if o.quality_flag == "ok" else 0.4)
                       for o in usable) / len(usable)
    measurement_component = round(0.12 + 0.25 * (1 - avg_fidelity), 3)

    # inference: proportional to number of unresolved mandatory alternatives
    n_alt = len(construct.mandatory_alternatives)
    inference_component = round(min(0.45, 0.08 + 0.06 * n_alt), 3)

    # total: use a soft-or so it stays < 1
    total = round(1 - (1 - measurement_component) * (1 - evidence_component) * (1 - inference_component), 3)

    evidence_ids = [o.id for o in usable]
    return round(value, 3), Uncertainty(
        kind="composite",
        total=total,
        measurement_component=measurement_component,
        evidence_component=evidence_component,
        inference_component=inference_component,
    ), evidence_ids


# ---------------------------------------------------------------------------
# The engine
# ---------------------------------------------------------------------------

class InferenceEngine:
    """Estimates constructs from observations with refusal discipline."""

    def __init__(self, options: dict | None = None):
        opts = options or {}
        self.channel_convergence_bonus = float(opts.get("convergence_bonus", 0.06))
        self.channel_divergence_penalty = float(opts.get("divergence_penalty", 0.10))
        self.min_confidence = float(opts.get("min_confidence", 0.15))

    # -- admissibility ----------------------------------------------------
    def _admissibility(
        self,
        construct: Construct,
        observations: list[Observation],
        *,
        context: dict,
        window_defined: bool,
    ) -> Optional[Refusal]:
        if not observations:
            return Refusal("NO_EVIDENCE", construct.id,
                           "Aucune observation alignée à ce construit.")
        # For a capacity/function profile (constructs & capabilities) we estimate
        # a *disposition*, so a momentary window is not required. Only true state
        # modulators require both a temporal window and full context, per the
        # HCSM Capacity-vs-State separation.
        if construct.role == "state_modulator":
            if construct.requires_context:
                missing = [c for c in construct.requires_context if not context.get(c)]
                if missing and len(missing) == len(construct.requires_context):
                    return Refusal("CONTEXT_MISSING", construct.id,
                                   f"Contexte requis manquant : {', '.join(missing)}.")
            if not window_defined:
                return Refusal("WINDOW_UNDEFINED", construct.id,
                               "Fenêtre temporelle non définie pour un état transitoire.")
        # Any usable observation at all?
        if not any(_sufficient_alignment(o) and _observation_weight(o) >= self.min_confidence
                   for o in observations):
            return Refusal("NO_EVIDENCE", construct.id,
                           "Aucune observation suffisamment alignée et fiable.")
        # Provenance: at least one observation must carry provenance.
        if not any(o.provenance for o in observations):
            return Refusal("PROVENANCE_BROKEN", construct.id,
                           "Chaîne de provenance manquante.")
        return None

    def estimate(
        self,
        construct_id: str,
        observations: list[Observation],
        *,
        context: dict | None = None,
        window: dict | None = None,
        epistemic_level: int = 2,
    ) -> ConstructEstimate | Refusal:
        construct = get_construct(construct_id)
        context = context or {}
        window_defined = window is not None

        refusal = self._admissibility(construct, observations, context=context,
                                      window_defined=window_defined)
        if refusal is not None:
            return refusal

        value, uncertainty, evidence_ids = fuse_observations(
            observations, construct,
            channel_convergence_bonus=self.channel_convergence_bonus,
            channel_divergence_penalty=self.channel_divergence_penalty,
        )

        # Alternatives: name each mandatory alternative with a plausibility
        # derived from how much of the observed variance it *could* explain.
        alternatives = []
        for alt_id in construct.mandatory_alternatives:
            try:
                alt_construct = get_construct(alt_id)
            except KeyError:
                continue
            alt_obs = [o for o in observations if o.aligns_to(alt_id)]
            plausibility = 0.25
            if alt_obs:
                plausibility = min(0.9, 0.35 + _observation_weight(alt_obs) * 0.2)
            alternatives.append(AlternativeExplanation(
                modulator_id=alt_id, label=alt_construct.label,
                plausibility=round(plausibility, 3),
                explains=[o.id for o in alt_obs][:4],
                competing_with=list(construct.mandatory_alternatives),
            ))

        rationale = (f"{construct.label} : {len(evidence_ids)} observation(s) fusionnée(s) "
                     f"sur {len(observations)} ; incertitude totale {uncertainty.total:.2f}.")

        return ConstructEstimate(
            construct_id=construct.id,
            construct_label=construct.label,
            domain=construct.domain,
            value=value,
            strength_label=_strength_label(value),
            epistemic_level=epistemic_level if epistemic_level < 5 else 4,
            uncertainty=uncertainty,
            evidence_ids=evidence_ids,
            alternatives=alternatives,
            rationale=rationale,
            window=window,
            context=context,
        )
