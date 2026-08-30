"""
Language-decoder — Evidence model
=================================

An *Observation* is a typed, provenanced, contextualised, temporally located
record that *may* enter an inference. It is not a proof and not a construct.

Rigour inherited from HCSM evidence model v0.1.0:

* Observation is never a Construct; it never carries a construct_id *directly*
  — it carries *alignment* to one or more constructs from the ontology.
* Missing data is explicit (not_collected / collected_unusable / refused_by_person).
* Channel is one of the RDoC-aligned evidence channels.
* `alignment` ∈ {exact, close, related, none}. An observation aligned `none`
  can be stored but can never found an estimate on its own.
* Provenance is mandatory: an agent (human/software/organisation), an activity
  type, and a source document/location when available.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .ontology import EVIDENCE_CHANNELS, MATCH_KINDS, get_construct

MISSINGNESS = ("not_collected", "collected_unusable", "refused_by_person")

QUALITY_FLAGS = ("ok", "degraded", "unusable")

AGENT_KINDS = ("human", "software", "organisation")

ACTIVITY_TYPES = ("MeasureActivity", "DecodeActivity", "InferenceActivity")


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class TemporalWindow:
    """A window centred on a time point. HCSM uses centre + half-width."""

    centre: str
    half_width: int = 0
    unit: str = "day"

    def __post_init__(self) -> None:
        if self.unit not in ("s", "min", "h", "day", "month", "year"):
            raise ValueError(f"Unknown window unit: {self.unit}")
        if self.half_width < 0:
            raise ValueError("half_width must be >= 0")


@dataclass(frozen=True)
class Provenance:
    agent: str
    agent_kind: str = "software"
    activity_type: str = "DecodeActivity"
    source_document: str = ""
    source_location: str = ""
    source_page: Optional[int] = None
    software_version: str = ""
    timestamp: str = field(default_factory=lambda: _now().isoformat())

    def __post_init__(self) -> None:
        if self.agent_kind not in AGENT_KINDS:
            raise ValueError(f"Unknown agent_kind: {self.agent_kind}")
        if self.activity_type not in ACTIVITY_TYPES:
            raise ValueError(f"Unknown activity_type: {self.activity_type}")


@dataclass
class Observation:
    """A single typed observation about a human, aligned to constructs."""

    id: str = field(default_factory=lambda: f"obs-{uuid.uuid4().hex[:12]}")
    construct_ids: tuple = ()          # construct ids from the ontology
    content: str = ""                  # raw textual content / value description
    channel: str = "subjective"
    alignment: str = "close"
    raw_value: Optional[float] = None
    normalized_value: Optional[float] = None
    confidence: float = 0.5            # 0..1 confidence in the *observation* (not the construct)
    missingness: str = ""
    quality_flag: str = "ok"
    window: Optional[TemporalWindow] = None
    context: dict = field(default_factory=dict)
    provenance: Optional[Provenance] = None
    epistemic_level: int = 1           # 1 fact … 5 psych conclusion (never auto for 5)
    source_span: str = ""              # the span of input text this was derived from

    def __post_init__(self) -> None:
        if self.channel not in EVIDENCE_CHANNELS:
            raise ValueError(f"Unknown channel: {self.channel}")
        if self.alignment not in MATCH_KINDS:
            raise ValueError(f"Unknown alignment: {self.alignment}")
        if self.quality_flag not in QUALITY_FLAGS:
            raise ValueError(f"Unknown quality_flag: {self.quality_flag}")
        if self.missingness and self.missingness not in MISSINGNESS:
            raise ValueError(f"Unknown missingness: {self.missingness}")
        if self.raw_value is None and not self.missingness and not self.content:
            raise ValueError("An observation needs a raw_value, a missingness, or content.")
        # validate construct ids exist
        if self.construct_ids:
            for cid in set(self.construct_ids):
                get_construct(cid)  # raises if unknown

    # -- helpers -----------------------------------------------------------
    def aligns_to(self, construct_id: str) -> bool:
        return construct_id in self.construct_ids

    def with_constructs(self, construct_ids) -> "Observation":
        self.construct_ids = tuple(dict.fromkeys(construct_ids))
        return self

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "construct_ids": list(self.construct_ids),
            "content": self.content,
            "channel": self.channel,
            "alignment": self.alignment,
            "raw_value": self.raw_value,
            "normalized_value": self.normalized_value,
            "confidence": round(self.confidence, 3),
            "missingness": self.missingness,
            "quality_flag": self.quality_flag,
            "window": None if not self.window else {
                "centre": self.window.centre, "half_width": self.window.half_width,
                "unit": self.window.unit,
            },
            "context": self.context,
            "provenance": None if not self.provenance else {
                "agent": self.provenance.agent,
                "agent_kind": self.provenance.agent_kind,
                "activity_type": self.provenance.activity_type,
                "source_document": self.provenance.source_document,
                "source_location": self.provenance.source_location,
                "source_page": self.provenance.source_page,
                "software_version": self.provenance.software_version,
                "timestamp": self.provenance.timestamp,
            },
            "epistemic_level": self.epistemic_level,
            "source_span": self.source_span,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Observation":
        prov = d.get("provenance")
        if prov:
            prov = Provenance(
                agent=prov["agent"], agent_kind=prov.get("agent_kind", "software"),
                activity_type=prov.get("activity_type", "DecodeActivity"),
                source_document=prov.get("source_document", ""),
                source_location=prov.get("source_location", ""),
                source_page=prov.get("source_page"),
                software_version=prov.get("software_version", ""),
                timestamp=prov.get("timestamp"),
            )
        win = d.get("window")
        if win:
            win = TemporalWindow(centre=win["centre"], half_width=win["half_width"],
                                 unit=win["unit"])
        return cls(
            id=d["id"], construct_ids=tuple(d.get("construct_ids", ())),
            content=d.get("content", ""), channel=d.get("channel", "subjective"),
            alignment=d.get("alignment", "close"),
            raw_value=d.get("raw_value"), normalized_value=d.get("normalized_value"),
            confidence=d.get("confidence", 0.5), missingness=d.get("missingness", ""),
            quality_flag=d.get("quality_flag", "ok"), window=win,
            context=d.get("context", {}), provenance=prov,
            epistemic_level=d.get("epistemic_level", 1), source_span=d.get("source_span", ""),
        )
