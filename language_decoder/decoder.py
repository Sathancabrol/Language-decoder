"""
Language-decoder — Decoder (text -> evidence)
=============================================

Turns natural-language descriptions of a human into *typed, aligned,
provenanced Observations* that the inference engine can consume.

Three decode paths, all producing the same Observation contract:

  * `decode_text`    — deterministic lexical decoder for free narrative /
                       CV / interview text. Pure stdlib, offline.
  * `decode_items`   — structured input (questionnaire items, declarations),
                       each item is a (statement, strength, channel) tuple.
  * `decode_ai`      — adapter for an external LLM output (e.g. Gemini /
                       OpenAI) that returns a strict JSON schema of proposed
                       observations. Those arrive as proposals at epistemic
                       level 4 (hypothesis to be validated by the human), so the
                       "never auto-certify cognitive conclusions" rule holds.

Rigor:

  * Every observation names the construct(s) it *aligns to* (exact / close /
    related / none). `none` alignments never found an estimate alone.
  * Intensity modifiers (fort, bien, nettement, très, faiblement, un peu, …)
    modulate the normalized value.
  * Evidence type is inferred from the text's register (CV / project /
    declaration / measurement) -> channel + epistemic level.
  * A psych *conclusion* (level 5) is never produced automatically.
"""

from __future__ import annotations

import json
import re
from typing import Iterable

from .evidence import Observation, Provenance
from .ontology import BY_ID, get_construct

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

# Intensity modifiers, French + English, with signed magnitude in 0..1.
# Compiled up-front so they can be used with .finditer().
_INTENSITY = [
    (re.compile(r"\b(très|extrêmement|fortement|nettement|beaucoup|remarquablement|hautement|exceptionnellement|particulièrement)\b", re.IGNORECASE), +0.15),
    (re.compile(r"\b(assez|plutôt|modérément|raisonnablement|relativement)\b", re.IGNORECASE), +0.05),
    (re.compile(r"\b(légèrement|un peu|quelque peu|faiblement|modérément faible)\b", re.IGNORECASE), -0.05),
    (re.compile(r"\b(faiblement|peu|insuffisamment|difficilement|à peine|mal|médiocre|mauvais|"
                r"difficulté|problème avec|limite)\b", re.IGNORECASE), -0.12),
    (re.compile(r"\b(très|extremely|highly|strongly|remarkably|notably|particularly)\b", re.IGNORECASE), +0.15),
    (re.compile(r"\b(somewhat|moderately|fairly|rather|reasonably)\b", re.IGNORECASE), +0.05),
    (re.compile(r"\b(slightly|a bit|a little|weakly|hardly)\b", re.IGNORECASE), -0.08),
    (re.compile(r"\b(strong|high|remarkable|excellent|notable|exceptional)\b", re.IGNORECASE), +0.10),
    (re.compile(r"\b(weak|low|limited|basic|modest|average)\b", re.IGNORECASE), -0.05),
]

# Negation / absence markers that flip or flag.
_NEGATION = re.compile(
    r"\b(ne\s+\w+\s+pas|pas\s+de|aucun|aucune|sans|jamais|manque\s+de|difficulté\s+à|peine\s+à|"
    r"\b(no|none|without|lack of|struggles? to|difficulty)\b)",
    re.IGNORECASE,
)

# Absence / presence verbs that add mild confidence.
_PRESENCE = re.compile(r"\b(démontre|maîtrise|excelle|fait preuve|manifeste|développe|possède|mobilise|"
                       r"\b(demonstrates|masters|excels|exhibits|possesses|shows|leverages)\b)",
                       re.IGNORECASE)

# Evidence-register classifiers -> channel + base epistemic level.
_REGISTER = [
    # measurement-ish register
    (re.compile(r"\b(score|test|mesure|indice|pourcent|times|précision|précise|erreur|RT|ms|%)\b", re.IGNORECASE),
     "behavioral", 1),
    # physiological / health register
    (re.compile(r"\b(FC|HRV|sommeil|pouls|fréquence cardiaque|actigraphie|vo2|physique|force|endurance)\b", re.IGNORECASE),
     "physiological", 1),
    # CV / career register -> subjective/behavioural, fact-level from documents
    (re.compile(r"\b(CV|expérience|poste|mission|entreprise|diplôme|formation|projet|stage|chantier|"
                r"équipe|responsable|chef|encadrement)\b", re.IGNORECASE),
     "subjective", 1),
    # explicit self-report
    (re.compile(r"\b(je suis|je dirais|je me trouve|auto-évaluation|je pense|selon moi|je considère)\b", re.IGNORECASE),
     "subjective", 2),
]

# ---------------------------------------------------------------------------
# Lexicon assembly: longest-matching construct per surface marker
# ---------------------------------------------------------------------------

# Sort aliases by length descending so "mémoire de travail" beats "mémoire".
_ALIAS_PATTERNS = sorted(
    [(re.compile(re.escape(a), re.IGNORECASE), cid, a)
     for cid, c in BY_ID.items()
     for a in c.aliases if len(a) >= 3],
    key=lambda x: -len(x[2]),
)


def _constructs_for_span(text: str, start: int, end: int) -> list[tuple[str, str]]:
    """Return (construct_id, matched_alias) for markers in text[start:end]."""
    window = text[start:end]
    hits: dict[str, str] = {}
    for pattern, cid, alias in _ALIAS_PATTERNS:
        m = pattern.search(window)
        if m:
            hits.setdefault(cid, alias)
    return list(hits.items())


def _sentence_around(text: str, start: int, end: int) -> str:
    """Return the sentence/clause containing the marker span."""
    if not text:
        return ""
    left = 0
    right = len(text)
    # Sentence/clause boundaries. We scan forward/backward from the span.
    for i in range(start, -1, -1):
        if text[i] in ".!?;:,\n":
            left = i + 1
            break
    for i in range(end, len(text)):
        if text[i] in ".!?;:,\n":
            right = i
            break
    return text[left:right].strip()


def _normalize_from_span(text: str, start: int, end: int) -> tuple[float, bool]:
    """Compute normalized value + negation flag from the marker's *sentence*."""
    local = _sentence_around(text, start, end)
    if not local:
        local = text[max(0, start - 40):end + 40]

    magnitude = 0.0
    for pat, delta in _INTENSITY:
        for m in pat.finditer(local):
            magnitude += delta
    magnitude = max(-0.4, min(0.4, magnitude))

    negated = bool(_NEGATION.search(local))
    present = bool(_PRESENCE.search(local))

    base = 0.5
    if present:
        base = 0.68
    if negated:
        base = 0.32
    value = max(0.05, min(0.98, base + magnitude))
    return round(value, 3), negated


# ---------------------------------------------------------------------------
# Text decode
# ---------------------------------------------------------------------------

def decode_text(
    text: str,
    *,
    source: str = "narrative",
    source_document: str = "",
    agent: str = "language-decoder",
    software_version: str = "0.1.0",
) -> list[Observation]:
    """Deterministic lexical decode of free text into Observations."""
    observations: list[Observation] = []
    if not text:
        return observations

    for pattern, cid, alias in _ALIAS_PATTERNS:
        for m in pattern.finditer(text):
            value, negated = _normalize_from_span(text, m.start(), m.end())
            register, channel, base_level = _classify_register(text, m.start(), m.end())
            # Alignment: defaults to close; it can only tighten to exact when the
            # surface marker is the canonical construct label.
            alignment = "close"
            if text[m.start():m.end()].strip().lower() in {a.lower() for a in BY_ID[cid].aliases if a.lower() == BY_ID[cid].label.lower()}:
                alignment = "exact"
            observations.append(
                Observation(
                    construct_ids=(cid,),
                    content=text[m.start():m.end()] + (f" [intensité={value:.2f}]" if value != 0.5 else ""),
                    channel=channel,
                    alignment=alignment,
                    normalized_value=value,
                    confidence=0.75 if not negated else 0.5,
                    quality_flag="ok",
                    provenance=Provenance(
                        agent=agent, source_document=source_document or source,
                        source_location=f"{source}:{m.start()}:{m.end()}",
                        software_version=software_version,
                    ),
                    epistemic_level=base_level,
                    source_span=text[m.start():m.end()],
                )
            )

    # De-duplicate: keep the strongest observation per (construct_id, span).
    return _dedupe(observations)


def _classify_register(text: str, start: int, end: int) -> tuple[str, str, int]:
    """Return (register, channel, base_epistemic_level) for a marker."""
    local = text[max(0, start - 80):end + 80]
    for pattern, channel, level in _REGISTER:
        if pattern.search(local):
            # CV/experience register overrides channel to behavioural-lite but
            # keeps fact-level epistemic (level 1).
            return "cv" if channel == "subjective" else "measure", channel, level
    return "narrative", "subjective", 2


# ---------------------------------------------------------------------------
# Structured items decode
# ---------------------------------------------------------------------------

def decode_items(
    items: Iterable[dict],
    *,
    source_document: str = "questionnaire",
    agent: str = "language-decoder",
    software_version: str = "0.1.0",
) -> list[Observation]:
    """
    Decode structured (statement, strength, channel) items.

    Each item: { "statement": str, "strength": 0..1 | None, "channel": str,
                 "constructs": [str] | None, "missingness": str | None }
    """
    observations: list[Observation] = []
    for it in items:
        statement = it.get("statement", "")
        strength = it.get("strength")
        channel = it.get("channel", "subjective")
        if strength is None:
            # Try to read a strength from the statement text.
            value, _ = _normalize_from_span(statement, 0, len(statement))
        else:
            value = max(0.0, min(1.0, float(strength)))
        constructs = it.get("constructs") or [cid for cid, _ in _constructs_for_span(statement, 0, len(statement))]
        constructs = list(dict.fromkeys(constructs))
        if not constructs:
            # fallback: classify by alias anywhere in the statement
            for cid, c in BY_ID.items():
                if any(a.lower() in statement.lower() for a in c.aliases):
                    constructs.append(cid)
        missingness = it.get("missingness", "")
        observations.append(Observation(
            construct_ids=tuple(constructs),
            content=statement,
            channel=channel,
            alignment="close",
            normalized_value=value,
            confidence=float(it.get("confidence", 0.7)),
            missingness=missingness,
            quality_flag=it.get("quality_flag", "ok"),
            provenance=Provenance(agent=agent, source_document=source_document,
                                  software_version=software_version),
            epistemic_level=2 if not missingness else 1,
        ))
    return _dedupe(observations)


# ---------------------------------------------------------------------------
# AI proposal decode (LLM adapter, guarded)
# ---------------------------------------------------------------------------

# Machine contract for LLM proposals.
AI_SCHEMA = {
    "type": "object",
    "properties": {
        "observations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "construct_id": {"type": "string"},
                    "content": {"type": "string"},
                    "strength": {"type": "number"},
                    "channel": {"type": "string"},
                    "alignment": {"type": "string"},
                    "confidence": {"type": "number"},
                    "source_span": {"type": "string"},
                },
                "required": ["construct_id", "content"],
            },
        }
    },
    "required": ["observations"],
}


def decode_ai_json(
    model_output: str,
    *,
    source_document: str = "ai_inference",
    agent: str = "model",
    software_version: str = "0.1.0",
) -> list[Observation]:
    """
    Parse an LLM proposal (strict JSON) into *pending* observations.

    Guardrails:
      * unknown construct_id -> drop with a note.
      * produced epistemic level is capped at 4 (hypothesis). Level 5 (psych
        conclusion) is never granted by inference.
      * alignment 'none' allowed (stored, but can't found an estimate alone).
    """
    try:
        payload = json.loads(model_output)
    except json.JSONDecodeError:
        raise ValueError("decode_ai_json: model output is not valid JSON.")

    proposals = payload.get("observations", [])
    observations: list[Observation] = []
    for p in proposals:
        cid = p.get("construct_id", "")
        if cid not in BY_ID:
            continue  # unknown construct
        strength = p.get("strength", 0.5)
        alignment = p.get("alignment", "close")
        if alignment == "exact":
            # An LLM cannot trust itself to 'exact' on a latent construct.
            alignment = "close"
        observations.append(Observation(
            construct_ids=(cid,),
            content=p.get("content", ""),
            channel=p.get("channel", "subjective"),
            alignment=alignment,
            normalized_value=max(0.0, min(1.0, float(strength))),
            confidence=min(0.6, float(p.get("confidence", 0.5))),  # proposals capped
            provenance=Provenance(agent=agent, source_document=source_document,
                                  software_version=software_version),
            epistemic_level=4,  # hypothesis, always requires human validation
            source_span=p.get("source_span", ""),
        ))
    return observations


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dedupe(observations: list[Observation]) -> list[Observation]:
    """Keep the observation with the highest weight per (construct_id, span)."""
    best: dict[tuple, Observation] = {}
    for o in observations:
        key = (o.construct_ids, o.source_span or o.content)
        w = (o.confidence * {"exact": 1, "close": .7, "related": .4, "none": 0}.get(o.alignment, 0))
        if key not in best or w > best[key][0]:
            best[key] = (w, o)
    return [o for (w, o) in best.values()]


def group_by_construct(observations: list[Observation]) -> dict[str, list[Observation]]:
    groups: dict[str, list[Observation]] = {}
    for o in observations:
        for cid in o.construct_ids:
            groups.setdefault(cid, []).append(o)
    return groups
