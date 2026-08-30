"""
Language-decoder — Dynamics (functioning over time)
===================================================

How a human *functions* over time. This is the time dimension that turns a
snapshot DecodedHuman into a trajectory.

Theories used (literature-proven concepts, not ad-hoc):

  * Forgetting curve — Ebbinghaus (1885): exponential decay of memory,
    operationalised as an exponential half-life decay toward a residual
    crystallised floor (also the memory-decline view in Cognitorium decay.ts).
  * Power law of practice — Newell & Rosenbloom (1981): skill acquisition is
    power-law, so *reactivation* is much faster than first acquisition when the
    residue is above the floor.
  * Transfer — Thorndike & Woodworth (1901), near/far transfer: the reuse of a
    competence in a new context; a banded transferability score.
  * State vs trait — Steyer et al. / HCSM CapacityProfile: stable disposition
    (capacity) vs transient fluctuation (state); never collapsed.
  * Cognitive load & allostasis — Wickens, Kahneman: effort allocation as a
    dynamic modulator.

The engine is deterministic and stdlib-only. It never claims to predict the
future; it describes plausible functioning given observed history.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Decay / retention
# ---------------------------------------------------------------------------

@dataclass
class Retention:
    """Vitality of a competence/knowledge given time since last practice."""

    construct_id: str
    base_level: float          # 0..1 mastery at peak
    last_practiced_year: int
    half_life_years: float
    current_year: int
    retention_floor_ratio: float = 0.35   # crystallised memory floor (Ebbinghaus residue)
    reactivated: bool = False

    @property
    def years_inactive(self) -> int:
        return max(0, self.current_year - self.last_practiced_year)

    @property
    def retention_floor(self) -> float:
        return self.base_level * self.retention_floor_ratio

    def vitality(self) -> float:
        """Exponential decay toward the crystallised floor (Ebbinghaus)."""
        if self.reactivated:
            # Reactivation is far faster than first acquisition (power law):
            # return near peak immediately.
            return min(1.0, round(self.base_level * 0.96, 3))
        if self.years_inactive == 0:
            return round(self.base_level, 3)
        decayable = self.base_level - self.retention_floor
        multiplier = math.exp(-math.log(2) * (self.years_inactive / max(0.1, self.half_life_years)))
        value = self.retention_floor + decayable * multiplier
        return round(max(0.0, min(1.0, value)), 3)

    def availability_label(self) -> str:
        v = self.vitality()
        if v >= 0.80:
            return "Disponibilité immédiate"
        if v >= 0.55:
            return "En veille active"
        return "Dormante (cristallisée)"

    def reactivation_effort(self) -> dict:
        v = self.vitality()
        # power-law-like: effort scales with (1 - vitality)^-something
        if v >= 0.80:
            return {"days_to_reactivate": 1, "label": "Immédiat (< 24h)",
                    "advice": "Une mise en contexte suffit pour mobiliser le potentiel."}
        if v >= 0.55:
            return {"days_to_reactivate": 3, "label": "Rapide (2 à 5 jours)",
                    "advice": "Un court projet pratique réactive les automatismes."}
        return {"days_to_reactivate": 10, "label": "Moyen (1 à 2 semaines)",
                "advice": "Les bases restent en mémoire cristallisée ; une à deux semaines suffisent."}

    def as_dict(self) -> dict:
        return {
            "construct_id": self.construct_id,
            "base_level": round(self.base_level, 3),
            "last_practiced_year": self.last_practiced_year,
            "half_life_years": self.half_life_years,
            "current_year": self.current_year,
            "years_inactive": self.years_inactive,
            "vitality": self.vitality(),
            "availability_label": self.availability_label(),
            "retention_floor": round(self.retention_floor, 3),
            "reactivation_effort": self.reactivation_effort(),
        }


# ---------------------------------------------------------------------------
# Transfer
# ---------------------------------------------------------------------------

TRANSFER_BANDS = [
    (0.8, "Très transposable — forte généralisation inter-contexte"),
    (0.55, "Transposable — mobilisable dans des contextes proches"),
    (0.3, "Partiellement transposable — nécessite un pont"),
    (0.0, "Peu transposable — fortement ancré dans son contexte d'origine"),
]


def transferability(band: float) -> dict:
    band = max(0.0, min(1.0, band))
    label = "Transabilité"
    for threshold, text in TRANSFER_BANDS:
        if band >= threshold:
            label = text
            break
    return {"score": round(band, 3), "label": label}


# ---------------------------------------------------------------------------
# Learning curve (power law)
# ---------------------------------------------------------------------------

def learning_curve(base_level: float, learning_rate: float, trials_or_weeks: int) -> list[float]:
    """
    Power law of practice: mastery(t) = peak - (peak - start) * (1 + r*t)^-b.

    Return discrete values over trials/weeks. When learning_rate is small the
    curve is shallow; when large, it is steep. Deterministic.
    """
    start = 0.0
    peak = min(1.0, base_level)
    out = []
    for t in range(1, trials_or_weeks + 1):
        v = peak - (peak - start) * math.pow(1 + learning_rate * t, -0.4)
        out.append(round(max(0.0, min(1.0, v)), 3))
    return out


# ---------------------------------------------------------------------------
# State vs trait
# ---------------------------------------------------------------------------

@dataclass
class TraitStateSplit:
    """Separation of a stable disposition from a transient state for a construct."""

    construct_id: str
    trait: float        # underlying capacity, slow-moving
    state: float        # current fluctuation, fast-moving
    state_rationale: str = ""
    window: str = ""

    @property
    def is_state_dominant(self) -> bool:
        return abs(self.state) > abs(self.trait)

    def as_dict(self) -> dict:
        return {
            "construct_id": self.construct_id,
            "trait": round(self.trait, 3),
            "state": round(self.state, 3),
            "state_dominant": self.is_state_dominant,
            "window": self.window,
            "state_rationale": self.state_rationale,
        }


# ---------------------------------------------------------------------------
# Trajectory
# ---------------------------------------------------------------------------

@dataclass
class TrajectoryPoint:
    year: int
    value: float
    kind: str = "estimate"          # estimate | observation | projection (HYPOTHESIS)
    note: str = ""

    def as_dict(self) -> dict:
        return {"year": self.year, "value": round(self.value, 3), "kind": self.kind, "note": self.note}


@dataclass
class Trajectory:
    construct_id: str
    points: list = field(default_factory=list)

    def add(self, year: int, value: float, kind: str = "estimate", note: str = "") -> None:
        self.points.append(TrajectoryPoint(year, value, kind, note))
        self.points.sort(key=lambda p: p.year)

    def as_dict(self) -> dict:
        return {"construct_id": self.construct_id,
                "points": [p.as_dict() for p in self.points]}


# ---------------------------------------------------------------------------
# Convenience: build a dynamics bundle for a set of constructs
# ---------------------------------------------------------------------------

def build_dynamics(
    retentions: list[Retention],
    *,
    transfer_bands: dict[str, float] | None = None,
    current_year: int,
) -> dict:
    """Aggregate retention + transfer for the profile's `dynamics` section."""
    transfer_bands = transfer_bands or {}
    out = []
    for r in retentions:
        entry = r.as_dict()
        entry["transferability"] = transferability(transfer_bands.get(r.construct_id, 0.5))
        out.append(entry)
    return {
        "current_year": current_year,
        "retentions": out,
        "model": "Ebbinghaus forgetting curve + power-law reactivation; "
                 "see language_decoder.dynamics",
    }
