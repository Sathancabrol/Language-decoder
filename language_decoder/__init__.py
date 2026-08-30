"""
Language-decoder — Human decoding engine
========================================

Decodes the *human* — physical and mental characteristics, capacity for action,
and how it functions over time — into an auditable, UI-ready profile, grounded
in established ontologies (ICF, RDoC, Cognitive Atlas) and epistemic models.

Stack principles:
  * deterministic, offline, stdlib-only core (no ML dependency required)
  * optional AI adapter (decode_ai_json) that is capped and guarded
  * evidence/provenance first, never a bare score
  * never a level-5 psychological conclusion without a human
"""

from .ontology import Construct, BY_ID, DOMAINS, get_construct
from .evidence import Observation, Provenance, TemporalWindow
from .inference import InferenceEngine, ConstructEstimate, Refusal
from .profile import decode_human, DecodedHuman

VERSION = "0.1.0"

__all__ = [
    "VERSION",
    "Construct",
    "BY_ID",
    "DOMAINS",
    "get_construct",
    "Observation",
    "Provenance",
    "TemporalWindow",
    "InferenceEngine",
    "ConstructEstimate",
    "Refusal",
    "decode_human",
    "DecodedHuman",
]
