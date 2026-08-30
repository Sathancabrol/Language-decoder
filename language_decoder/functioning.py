"""
Language-decoder — Functioning (ICF bridge)
===========================================

Translates construct estimates into *functioning* statements against the ICF
(International Classification of Functioning, Disability and Health, WHO, 2001),
introducing the ICF's core separation — Capacity ⊥ Performance ⊥ Participation.

Rules inherited from HCSM functioning model v0.1.0:

  * A FunctionalProjection is always a HYPOTHESIS, never a deduction.
  * ConstructEstimate ≠ Capacity ≠ Performance ≠ Participation. ICF forbids a
    single rule to jump between them; we respect that.
  * We never produce a "global cognitive functioning score".
  * A low State is never automatically translated into a participation
    restriction, and never into a justification for a school/medical/managerial
    decision.

The projection is addressed only for the small, deliberately-opened ICF bridge
(b204, b140, b144, b164, b1300 for the physical/mental constructs; and d1-d9
activity codes for the action domain).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .ontology import get_construct

FUNCTION_KINDS = (
    "body_function",               # ICF b*
    "activity_hypothesis",         # ICF d*
    "participation_hypothesis",    # ICF d*/e* — always cautious
    "environment_factor",
)

# Small, opened bridge: construct -> ICF code(s) with nature.
# nature: 'body_function' | 'activity' — deliberately conservative.
_BRIDGE: dict[str, list[dict]] = {
    "mental_attention": [{"code": "b140", "nature": "body_function"}],
    "mental_working_memory": [{"code": "b144", "nature": "body_function"}],
    "mental_cognitive_control": [{"code": "b164", "nature": "body_function"}],
    "phys_strength_endurance": [{"code": "b730", "nature": "body_function"}],
    "phys_energy_sleep": [{"code": "b1300", "nature": "body_function"}],
    "mental_perception": [{"code": "b210-b280", "nature": "body_function"}],
    "mental_language": [{"code": "b167", "nature": "body_function"}],
    "mental_emotion": [{"code": "b152", "nature": "body_function"}],
    "act_savoir_faire": [{"code": "d2", "nature": "activity"}],
    "act_organize_coordinate": [{"code": "d2", "nature": "activity"}],
    "act_communicate_teach": [{"code": "d3", "nature": "activity"}],
    "act_adapt_improvise": [{"code": "d2", "nature": "activity"}],
    "act_sustained_action": [{"code": "d2", "nature": "activity"}],
    "act_leadership": [{"code": "d7", "nature": "activity"}],
    "mental_social_cognition": [{"code": "d7", "nature": "activity"}],
}

_DOES_NOT_IMPLY = [
    "diagnostic",
    "restriction de participation",
    "besoin de traitement",
    "décision scolaire, médicale ou managériale",
    "jugement clinique",
]


@dataclass
class FunctionalProjection:
    construct_id: str
    target_code: str             # ICF code (or short form)
    kind: str = "body_function"
    status: str = "HYPOTHESIS"
    value: Optional[float] = None
    about: str = ""
    does_not_imply: list = field(default_factory=lambda: list(_DOES_NOT_IMPLY))

    def __post_init__(self) -> None:
        if self.kind not in FUNCTION_KINDS:
            raise ValueError(f"Unknown function kind: {self.kind}")
        if self.status != "HYPOTHESIS":
            raise ValueError("FunctionalProjection.status is always HYPOTHESIS (ICF discipline).")

    def as_dict(self) -> dict:
        return {
            "construct_id": self.construct_id,
            "target_code": self.target_code,
            "kind": self.kind,
            "status": self.status,
            "value": None if self.value is None else round(self.value, 3),
            "about": self.about,
            "does_not_imply": self.does_not_imply,
        }


def project(function_estimates: list[dict], *, context_complete: bool = True) -> list[FunctionalProjection]:
    """
    Build ICF projections from construct estimates.

    `function_estimates`: list of {construct_id, value, label, domain}.
    Any estimate without a bridge entry is omitted (that's fine — we only open
    a small, well-documented bridge, per HCSM).
    """
    projections: list[FunctionalProjection] = []
    for est in function_estimates:
        cid = est.get("construct_id")
        if cid not in _BRIDGE:
            continue
        for bridge in _BRIDGE[cid]:
            nature = bridge["nature"]
            kind = "body_function" if nature == "body_function" else "activity_hypothesis"
            projections.append(FunctionalProjection(
                construct_id=cid,
                target_code=bridge["code"],
                kind=kind,
                value=est.get("value"),
                about=f"Projection de {est.get('label', cid)} vers ICF {bridge['code']} — hypothèse, pas déduction.",
            ))
    return projections
