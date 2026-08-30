"""Tests for the Language-decoder engine (deterministic, stdlib-only)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from language_decoder import decode_human, BY_ID, get_construct  # noqa: E402
from language_decoder.ontology import constructs_by_domain, DOMAINS  # noqa: E402
from language_decoder.inference import InferenceEngine  # noqa: E402
from language_decoder.evidence import Observation, Provenance, TemporalWindow  # noqa: E402
from language_decoder.dynamics import Retention, transferability  # noqa: E402


# ---------------------------------------------------------------------------
# Ontology
# ---------------------------------------------------------------------------

def test_ontology_has_4_domains():
    assert set(DOMAINS) == {"physical", "mental", "action", "dynamics"}
    assert constructs_by_domain("mental")
    assert constructs_by_domain("physical")
    assert constructs_by_domain("action")
    assert constructs_by_domain("dynamics")


def test_ontology_every_construct_has_external_alignment():
    for cid, c in BY_ID.items():
        assert c.external_alignment is not None, f"{cid} lacks external alignment"
        assert c.status in ("ESTABLISHED", "SUPPORTED", "PROPOSED")
        assert c.label


def test_ontology_attention_alternatives():
    att = get_construct("mental_attention")
    assert "phys_energy_sleep" in att.mandatory_alternatives
    assert att.external_alignment.match in ("exact", "close")


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

def test_observation_requires_content_or_value():
    try:
        Observation(construct_ids=("mental_attention",), channel="subjective")
        assert False, "should have raised"
    except ValueError:
        pass


def test_observation_rejects_unknown_construct():
    try:
        Observation(construct_ids=("nope",), content="x")
        assert False
    except KeyError:
        pass


def test_observation_roundtrip_dict():
    o = Observation(construct_ids=("mental_attention",), content="forte concentration",
                    channel="subjective", normalized_value=0.8,
                    provenance=Provenance(agent="test", source_document="cv"))
    d = o.as_dict()
    o2 = Observation.from_dict(d)
    assert o2.construct_ids == o.construct_ids
    assert o2.provenance.agent == "test"


# ---------------------------------------------------------------------------
# Decoder (text)
# ---------------------------------------------------------------------------

def test_decode_text_detects_mental_and_action():
    text = ("Elle démontre une très forte concentration et une grande capacité "
            "à organiser et coordonner un chantier. Elle est également très "
            "résistante physiquement, avec une bonne endurance.")
    obs = decode_human(text=text)
    cids = set()
    for o in obs.observations:
        cids.update(o["construct_ids"])
    assert "mental_attention" in cids
    assert "act_organize_coordinate" in cids
    assert "phys_strength_endurance" in cids


def test_decode_text_intensity_changes_value():
    text_low = "Il a peu de concentration."
    text_high = "Il a une très forte concentration."
    h_low = decode_human(text=text_low)
    h_high = decode_human(text=text_high)
    v_low = _value_for(h_low, "mental_attention")
    v_high = _value_for(h_high, "mental_attention")
    assert v_high > v_low


def _value_for(profile, cid):
    for d in profile.domains.values():
        for e in d.estimates:
            if e["construct_id"] == cid:
                return e["value"]
    return None


# ---------------------------------------------------------------------------
# Inference / refusal discipline
# ---------------------------------------------------------------------------

def test_no_evidence_refusal():
    engine = InferenceEngine()
    # construct with no observations alongside others; we directly test engine
    result = engine.estimate("mental_working_memory", [])
    assert result.code == "NO_EVIDENCE"


def test_weak_alignment_cannot_estimate():
    engine = InferenceEngine()
    o = Observation(construct_ids=("mental_attention",), content="mention",
                    channel="digital_passive", alignment="none",
                    confidence=0.9, normalized_value=0.9,
                    provenance=Provenance(agent="t"))
    result = engine.estimate("mental_attention", [o])
    assert result.code == "NO_EVIDENCE"


def test_valid_estimate_has_uncertainty_and_alternatives():
    engine = InferenceEngine()
    o1 = Observation(construct_ids=("mental_attention",), content="CPT omissions 2%",
                     channel="behavioral", alignment="close", normalized_value=0.8,
                     confidence=0.9, provenance=Provenance(agent="t", source_document="lab"))
    o2 = Observation(construct_ids=("mental_attention",), content="auto-rapport focus",
                     channel="subjective", alignment="close", normalized_value=0.7,
                     confidence=0.7, provenance=Provenance(agent="t", source_document="ema"))
    est = engine.estimate("mental_attention", [o1, o2], context={"task": "CPT"})
    assert est.estimate_status == "estimated"
    assert 0 <= est.value <= 1
    assert est.uncertainty.total > 0
    assert est.alternatives  # mandatory alternatives named
    assert est.epistemic_level < 5


# ---------------------------------------------------------------------------
# AI adapter guardrails
# ---------------------------------------------------------------------------

def test_decode_ai_never_level5_and_caps_alignment():
    from language_decoder.decoder import decode_ai_json
    payload = json.dumps({"observations": [
        {"construct_id": "mental_attention", "content": "attention soutenue",
         "strength": 0.9, "alignment": "exact", "confidence": 0.95},
    ]})
    obs = decode_ai_json(payload)
    assert len(obs) == 1
    assert obs[0].alignment in ("close", "related")  # exact downgraded
    assert obs[0].epistemic_level == 4
    assert obs[0].confidence <= 0.6


def test_decode_ai_drops_unknown_construct():
    from language_decoder.decoder import decode_ai_json
    payload = json.dumps({"observations": [
        {"construct_id": "nope", "content": "x"},
    ]})
    assert decode_ai_json(payload) == []


# ---------------------------------------------------------------------------
# Dynamics
# ---------------------------------------------------------------------------

def test_retention_decays_toward_floor():
    r = Retention("act_savoir_faire", base_level=0.9, last_practiced_year=2016,
                  half_life_years=5, current_year=2026)
    assert r.vitality() < r.base_level
    assert r.vitality() >= r.retention_floor - 0.05
    assert r.availability_label() in ("Disponibilité immédiate", "En veille active",
                                      "Dormante (cristallisée)")


def test_reactivation_returns_near_peak():
    r = Retention("act_savoir_faire", base_level=0.9, last_practiced_year=2000,
                  half_life_years=4, current_year=2026, reactivated=True)
    assert r.vitality() > 0.8


def test_transferability_bands():
    low = transferability(0.1)["label"]
    high = transferability(0.9)["label"]
    assert low != high
    assert "transposable" in high.lower()


# ---------------------------------------------------------------------------
# Pipeline / profile UI contract
# ---------------------------------------------------------------------------

def test_full_pipeline_produces_ui_contract():
    text = (
        "Ingénieur de recherche avec une très forte capacité d'analyse et de "
        "raisonnement. Il organise et anime des équipes pluridisciplinaires. "
        "Il maîtrise la programmation Python et la modélisation statistique. "
        "Cordiste expérimenté, il possède une excellente condition physique et "
        "une grande endurance. Il apprend vite et transpose ses compétences "
        "d'un domaine à l'autre."
    )
    profile = decode_human(text=text, person_id="h-bench", current_year=2026)
    data = profile.as_dict()

    assert set(data["domains"].keys()) == set(DOMAINS)
    # top-level UI keys
    for key in ("epistemic_summary", "ui_hints", "functioning", "dynamics",
                "observations", "refusals"):
        assert key in data
    # epistemic guard
    assert data["epistemic_summary"]["level5_present"] is False
    # functioning projections are hypotheses
    if data["functioning"]:
        assert all(f["status"] == "HYPOTHESIS" for f in data["functioning"])
    # any refused construct still recorded
    assert isinstance(data["refusals"], list)
    # JSON serialisable
    json.dumps(data)


def test_empty_input_produces_empty_but_valid_profile():
    profile = decode_human(text="", person_id="empty")
    data = profile.as_dict()
    assert data["epistemic_summary"]["total_estimates"] == 0
    assert "notes" in data


# ---------------------------------------------------------------------------
# Structured items
# ---------------------------------------------------------------------------

def test_decode_items():
    items = [
        {"statement": "Je maintiens mon attention plus de 2h", "strength": 0.8,
         "channel": "subjective", "constructs": ["mental_attention"]},
        {"statement": "Je gère les conflits d'équipe", "strength": 0.7,
         "channel": "subjective", "constructs": ["mental_social_cognition"]},
    ]
    profile = decode_human(items=items, person_id="h-items")
    cids = {c for o in profile.observations for c in o["construct_ids"]}
    assert "mental_attention" in cids
    assert "mental_social_cognition" in cids


if __name__ == "__main__":
    raise SystemExit("Run with pytest: python -m pytest tests/ -q")
