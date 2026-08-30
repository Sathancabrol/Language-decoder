"""
Language-decoder — Ontology (knowledge graph)
=============================================

What CAN be decoded about a human. This is deliberately a *knowledge* layer:
it does not say anything about a specific person. It only defines the set of
latent constructs (physical, mental, action, dynamics) that the inference
engine is allowed to estimate, together with how each maps onto established
external ontologies (Cognitive Atlas, RDoC, ICF, HPO) and its epistemic
properties.

Design rules (inherited from HCSM ontology v0.1.0):

* Observation is never a subclass of Construct.
* Every construct carries at least one external alignment (exact / close).
* Every construct carries an epistemic status and a typical timescale.
* No construct is a diagnostic code. Diagnosis is out of scope.
* `status` vocabulary: ESTABLISHED / SUPPORTED / PROPOSED / HYPOTHESIS /
  OPEN_QUESTION.

The four top-level domains mirror the request "décoder l'humain":

  1. physical  — characteristics of the body (ICF body functions b*, anthropometrics).
  2. mental    — cognitive & affective processes (RDoC / Cognitive Atlas / cognitive psychology).
  3. action    — capacity for action (CAPABILITY / capacity, ICF activities d*, skills, know-how).
  4. dynamics  — how the human functions over time (state vs trait, decay, transfer, learning).

Domain separation is strict: a physical construct never estimates a mental one
and vice versa; cross-domain influence is expressed as modulation, never as
identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------

DOMAINS = ("physical", "mental", "action", "dynamics")

STATUS_VOCABULARY = (
    "ESTABLISHED",
    "SUPPORTED",
    "PROPOSED",
    "HYPOTHESIS",
    "OPEN_QUESTION",
)

EXTERNAL_SOURCES = ("cognitive_atlas", "rdoc", "icf", "hpo", "cogpo")

MATCH_KINDS = ("exact", "close", "related", "none")

EVIDENCE_CHANNELS = (
    "behavioral",       # observable action / task outcome
    "subjective",       # self-report, interview, narrative
    "physiological",    # HRV, cortisol, actigraphy
    "neural",           # EEG, pupillometry
    "contextual",       # sleep, load, environment
    "computational",    # model parameters (DDM, RL)
    "digital_passive",  # GPS, screen-time, logs
)

TIMESCALES = ("momentary", "daily", "episodic", "dispositional")

CONTEXT_DIMENSIONS = (
    "task",
    "environment",
    "somatic",
    "occupational",
    "social",
    "temporal_structure",
    "motivational",
)


@dataclass(frozen=True)
class ExternalMapping:
    """An alignment of a construct onto an external ontology."""

    source: str
    source_iri: str
    match: str

    def __post_init__(self) -> None:
        if self.source not in EXTERNAL_SOURCES:
            raise ValueError(f"Unknown external source: {self.source}")
        if self.match not in MATCH_KINDS:
            raise ValueError(f"Unknown match kind: {self.match}")


@dataclass(frozen=True)
class Construct:
    """A latent construct the engine is allowed to estimate about a human."""

    id: str
    label: str
    domain: str
    description: str = ""
    status: str = "PROPOSED"
    typical_timescale: str = "dispositional"
    requires_context: tuple = ()
    mandatory_alternatives: tuple = ()
    mappings: tuple = ()
    modulators: tuple = ()
    evidence_channels: tuple = ()
    role: str = "construct"          # 'construct' | 'state_modulator' | 'trait' | 'capability'
    aliases: tuple = ()              # French / English surface markers used by the decoder

    def __post_init__(self) -> None:
        if self.domain not in DOMAINS:
            raise ValueError(f"Unknown domain for '{self.id}': {self.domain}")
        if self.status not in STATUS_VOCABULARY:
            raise ValueError(f"Unknown status for '{self.id}': {self.status}")
        # Allow tuple/list forms on dataclass input
        for name in ("requires_context", "mandatory_alternatives", "mappings",
                     "modulators", "evidence_channels", "aliases"):
            value = getattr(self, name)
            if isinstance(value, list):
                object.__setattr__(self, name, tuple(value))

    # -- convenience -------------------------------------------------------
    @property
    def external_alignment(self) -> Optional[ExternalMapping]:
        """Highest-priority external alignment (exact > close > related)."""
        for preferred in ("exact", "close", "related"):
            for m in self.mappings:
                if m.match == preferred:
                    return m
        return None


# ===========================================================================
# Seeded from the repository corpus. Sources of truth:
#   - HCSM ontology v0.1.0 (labels, ICF/RDoC/Cognitive Atlas mappings, statuses)
#   - proto-cognitorium psychologyAtlas & epistemics (cognitive taxonomy)
#   - ETAT-DE-LART-PSYCHOLOGIE / TAXONOMIE_PSYCHOLOGIE_COGNITIVE.md
#   - reaserch-engine glossary (capability / evidence distinctions)
# ===========================================================================

# Values are written as dicts then coerced to Construct for readability.
_RAW: list[dict] = [
    # ------------------------------------------------------------------
    # PHYSICAL — body functions & characteristics (ICF *b* codes)
    # ------------------------------------------------------------------
    dict(
        id="phys_sensorimotor",
        label="Sensori-moteur",
        domain="physical",
        description="Cohérence perception–action : vision, audition, proprioception, coordination motrice, dextérité.",
        status="ESTABLISHED",
        typical_timescale="dispositional",
        role="capability",
        mappings=[dict(source="icf", source_iri="icf:b210-b280", match="close")],
        evidence_channels=("behavioral", "physiological", "subjective"),
        aliases=("sensori-moteur", "motricité", "dextérité", "coordination", "manualité",
                 "sensorimotor", "dexterity", "motor", "gestuelle", "précision gestuelle"),
    ),
    dict(
        id="phys_strength_endurance",
        label="Force & endurance physique",
        domain="physical",
        description="Capacité à produire de la force et à la maintenir dans le temps (musculaire, cardio-respiratoire).",
        status="SUPPORTED",
        typical_timescale="episodic",
        role="capability",
        mappings=[dict(source="icf", source_iri="icf:b730", match="close")],
        evidence_channels=("behavioral", "physiological", "subjective"),
        aliases=("force", "endurance", "résistance", "port", "effort physique", "physique",
                 "strength", "endurance", "stamina", "corde", "cordiste", "terrassement"),
    ),
    dict(
        id="phys_energy_sleep",
        label="Niveau d'énergie & sommeil",
        domain="physical",
        description="Énergie, éveil, rythme veille-sommeil et récupération — modulateur physique de la performance.",
        status="SUPPORTED",
        typical_timescale="daily",
        role="state_modulator",
        requires_context=("somatic", "temporal_structure"),
        mappings=[dict(source="icf", source_iri="icf:b1300", match="close")],
        modulators=("mental_attention", "mental_cognitive_control", "phys_strength_endurance"),
        aliases=("fatigue", "énergie", "énergie", "sommeil", "récupération", "épuisement",
                 "fatigue", "energy", "sleep", "tiredness", "couché", "réveil"),
    ),
    dict(
        id="phys_health_security",
        label="État de santé & sécurité",
        domain="physical",
        description="Biomécanique, santé fonctionnelle et conditions de sécurité physique (port, gestes, environnement).",
        status="SUPPORTED",
        typical_timescale="episodic",
        role="construct",
        mappings=[dict(source="icf", source_iri="icf:b1", match="related"),
                  dict(source="hpo", source_iri="hp:0000001", match="related")],
        evidence_channels=("subjective", "contextual", "physiological"),
        aliases=("santé", "sécurité", "hygiène", "HSE", "risque", "accident", "condition physique",
                 "health", "safety", "PSE", "secourisme", "BNSSA"),
    ),
    dict(
        id="phys_anthropometric",
        label="Anthropométrie",
        domain="physical",
        description="Dimensions corporelles statiques (taille, masse, morphologie) — descripteur contextuel, non inférentiel de capacité.",
        status="ESTABLISHED",
        typical_timescale="dispositional",
        role="descriptor",
        mappings=[dict(source="icf", source_iri="icf:b530", match="related")],
        evidence_channels=("subjective", "physiological"),
        aliases=("taille", "poids", "morphologie", "stature", "corpulence"),
    ),

    # ------------------------------------------------------------------
    # MENTAL — processes (Broadly RDoC / Cognitive Atlas / cognitive psychology)
    # ------------------------------------------------------------------
    dict(
        id="mental_perception",
        label="Perception",
        domain="mental",
        description="Extraction d'information par les sens (visuelle, auditive, multisensorielle, perception-action).",
        status="ESTABLISHED",
        typical_timescale="momentary",
        role="construct",
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:perception", match="exact"),
                  dict(source="rdoc", source_iri="rdoc:cognitive_systems/visual_perception", match="close")],
        evidence_channels=("behavioral", "subjective", "physiological"),
        aliases=("perception", "vision", "audition", "écoute", "observation", "analyse visuelle",
                 "perception", "picture"),
    ),
    dict(
        id="mental_attention",
        label="Attention",
        domain="mental",
        description="Sélection, maintien et partage des ressources attentionnelles ; contrôle attentionnel.",
        status="ESTABLISHED",
        typical_timescale="momentary",
        role="construct",
        requires_context=("task",),
        mandatory_alternatives=("phys_energy_sleep", "mental_emotion", "mental_motivation",
                                "mental_cognitive_load", "phys_sleep_pressure"),
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:attention", match="exact"),
                  dict(source="rdoc", source_iri="rdoc:cognitive_systems", match="close"),
                  dict(source="icf", source_iri="icf:b140", match="close")],
        evidence_channels=("behavioral", "subjective", "physiological", "neural", "digital_passive"),
        aliases=("attention", "concentration", "vigilance", "focus", "surveillance", "soutenue",
                 "attention", "propreté d'esprit", "rester concentré", "observation fine"),
    ),
    dict(
        id="mental_working_memory",
        label="Mémoire de travail",
        domain="mental",
        description="Maintien et manipulation de l'information à court terme ; boucle phonologique, calepin visuo-spatial, administrateur central.",
        status="ESTABLISHED",
        typical_timescale="momentary",
        role="construct",
        requires_context=("task",),
        mandatory_alternatives=("mental_attention", "mental_cognitive_control", "mental_motivation",
                                "phys_energy_sleep"),
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:working_memory", match="exact"),
                  dict(source="rdoc", source_iri="rdoc:cognitive_systems", match="close"),
                  dict(source="icf", source_iri="icf:b144", match="close")],
        evidence_channels=("behavioral", "subjective", "neural"),
        aliases=("mémoire de travail", "mémoire à court terme", "working memory", "MCT",
                 "retenir", "manipuler", "charge mentale immédiate"),
    ),
    dict(
        id="mental_long_term_memory",
        label="Mémoire à long terme",
        domain="mental",
        description="Mémoire épisodique, sémantique et procédurale ; apprentissage, consolidation, rappel.",
        status="ESTABLISHED",
        typical_timescale="dispositional",
        role="construct",
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:long_term_memory", match="exact"),
                  dict(source="icf", source_iri="icf:b144", match="close")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("mémoire", "rappel", "rétention", "automatisme", "savoir-faire acquis",
                 "memory", "recall", "connaissances", "culture générale"),
    ),
    dict(
        id="mental_language",
        label="Langage & communication",
        domain="mental",
        description="Compréhension et production du langage ; syntaxe, sémantique, pragmatique.",
        status="ESTABLISHED",
        typical_timescale="dispositional",
        role="construct",
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:language", match="exact")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("langage", "langues", "bilingue", "anglais", "français", "communication", "phrasing",
                 "language", "parler", "rédaction", "écriture", "oral", "présentation",
                 "traduction"),
    ),
    dict(
        id="mental_reasoning",
        label="Raisonnement & résolution de problèmes",
        domain="mental",
        description="Induction, déduction, catégorisation, résolution de problèmes et créativité.",
        status="ESTABLISHED",
        typical_timescale="momentary",
        role="construct",
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:reasoning", match="exact"),
                  dict(source="rdoc", source_iri="rdoc:cognitive_systems", match="close")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("raisonnement", "analyse", "problème", "résolution", "logique", "diagnostic",
                 "synthèse", "concept", "modéliser", "abstraction", "heuristique", "insight",
                 "reasoning", "problem-solving", "analyse", "mettre en œuvre"),
    ),
    dict(
        id="mental_decision",
        label="Décision & jugement",
        domain="mental",
        description="Jugement, prises de décision, gestion du risque et de l'incertitude.",
        status="SUPPORTED",
        typical_timescale="momentary",
        role="construct",
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:decision_making", match="close")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("décision", "jugement", "arbitrage", "risque", "choix", "trancher",
                 "decision", "judgment", "gestion des priorités"),
    ),
    dict(
        id="mental_cognitive_control",
        label="Contrôle cognitif (fonctions exécutives)",
        domain="mental",
        description="Inhibition, flexibilité, mise à jour ; planification et régulation de l'action.",
        status="ESTABLISHED",
        typical_timescale="momentary",
        role="construct",
        requires_context=("task",),
        mandatory_alternatives=("mental_attention", "mental_working_memory", "mental_motivation",
                                "phys_energy_sleep"),
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:cognitive_control", match="close"),
                  dict(source="rdoc", source_iri="rdoc:cognitive_systems", match="exact"),
                  dict(source="icf", source_iri="icf:b164", match="close")],
        evidence_channels=("behavioral", "subjective", "neural"),
        aliases=("fonctions exécutives", "contrôle inhibiteur", "flexibilité", "planification",
                 "organisation", "adaptation", "régulation", "inhibition", "priorisation",
                 "executive", "planifier", "cadrer"),
    ),
    dict(
        id="mental_metacognition",
        label="Métacognition & auto-régulation",
        domain="mental",
        description="Connaissance et régulation de ses propres processus cognitifs ; planification, monitoring, contrôle.",
        status="SUPPORTED",
        typical_timescale="dispositional",
        role="construct",
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:metacognition", match="close")],
        evidence_channels=("subjective", "behavioral"),
        aliases=("métacognition", "auto-régulation", "auto-évaluation", "recul", "conscience de soi",
                 "monitoring", "régulation", "apprendre à apprendre", "SRL", "self-regulated"),
    ),
    dict(
        id="mental_emotion",
        label="Émotion & régulation émotionnelle",
        domain="mental",
        description="Perception, expression et régulation des émotions ; affect et humeur (état).",
        status="SUPPORTED",
        typical_timescale="daily",
        role="state_modulator",
        requires_context=("somatic", "social"),
        mappings=[dict(source="rdoc", source_iri="rdoc:negative_valence_systems", match="close"),
                  dict(source="cognitive_atlas", source_iri="cogatlas:emotion", match="close")],
        modulators=("mental_attention", "mental_reasoning", "mental_decision"),
        aliases=("émotion", "stress", "anxiété", "calme", "empathie", "gestion émotionnelle",
                 "contrôle de soi", "emotional", "stress", "résilience", "motion"),
    ),
    dict(
        id="mental_emotion_regulation",
        label="Régulation émotionnelle",
        domain="mental",
        description="Capacité *dispositionnelle* à réguler ses émotions et à gérer la pression — distincte de l'état émotionnel transitoire.",
        status="SUPPORTED",
        typical_timescale="dispositional",
        role="construct",
        mappings=[dict(source="rdoc", source_iri="rdoc:negative_valence_systems", match="close")],
        evidence_channels=("behavioral", "subjective", "contextual"),
        aliases=("régulation émotionnelle", "gestion du stress", "gère mal le stress",
                 "gérer le stress", "gestion de la pression", "contrôle émotionnel",
                 "garde son calme", "sous pression", "émotionnel", "maîtrise de soi",
                 "emotional regulation", "stress management", "composure"),
    ),
    dict(
        id="mental_motivation",
        label="Motivation & engagement",
        domain="mental",
        description="Direction, intensité et persistance du comportement ; intérêt, sens, engagement.",
        status="SUPPORTED",
        typical_timescale="daily",
        role="state_modulator",
        requires_context=("motivational",),
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:motivation", match="close")],
        modulators=("mental_attention", "mental_cognitive_control", "mental_persistence"),
        aliases=("motivation", "engagement", "persévérance", "intérêt", "sens", "passion",
                 "envie", "determination", "engagement", "proactivité", "drive"),
    ),
    dict(
        id="mental_social_cognition",
        label="Cognition sociale & relationnelle",
        domain="mental",
        description="Théorie de l'esprit, perception sociale, inférence sur autrui, gestes relationnels.",
        status="SUPPORTED",
        typical_timescale="dispositional",
        role="construct",
        mappings=[dict(source="rdoc", source_iri="rdoc:social_processes", match="close"),
                  dict(source="cognitive_atlas", source_iri="cogatlas:social_cognition", match="close")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("empathie", "empathique", "écoute", "relation", "travail en équipe", "coopération",
                 "négociation", "médiation", "transmission", "encadrement", "management",
                 "social", "communication", "collectif", "accompagner", "animer"),
    ),
    dict(
        id="mental_spatial_numeric",
        label="Cognition spatiale & numérique",
        domain="mental",
        description="Représentation de l'espace et des nombres ; navigation, rotation mentale, calcul.",
        status="SUPPORTED",
        typical_timescale="dispositional",
        role="construct",
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:spatial", match="close")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("spatial", "orientation", "cartes", "plans", "géométrie", "mesure",
                 "calcul", "chiffres", "statistiques", "données", "spatial", "topographie",
                 "statistiques", "modélisation statistique", "analyse de données"),
    ),

    # ------------------------------------------------------------------
    # ACTION — capacity for action (skills, capability, ICF activities d*)
    # ------------------------------------------------------------------
    dict(
        id="act_savoir_faire",
        label="Savoir-faire technique",
        domain="action",
        description="Mise en œuvre opérationnelle de procédures et d'outils concrets.",
        status="ESTABLISHED",
        typical_timescale="dispositional",
        role="capability",
        mappings=[dict(source="icf", source_iri="icf:d2", match="close"),
                  dict(source="cogpo", source_iri="cogpo:procedure", match="close")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("savoir-faire", "technique", "manipulation", "outil", "procédure", "logiciel",
                 "machin", "méthode", "exécution", "pratique", "compétence", "skill",
                 "programmation", "python", "développement", "code", "modélisation", "statistique",
                 "data", "outils", "machines", "équipement"),
    ),
    dict(
        id="act_organize_coordinate",
        label="Organisation & coordination",
        domain="action",
        description="Pilotage de tâches multiples, de ressources et d'acteurs ; coordination systémique.",
        status="SUPPORTED",
        typical_timescale="dispositional",
        role="capability",
        mappings=[dict(source="icf", source_iri="icf:d2", match="close")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("organiser", "coordonner", "pilotage", "gestion", "chef", "conduite", "chantier",
                 "responsable", "superviser", "ordonner", "orchestrer", "coordination", "manage"),
    ),
    dict(
        id="act_communicate_teach",
        label="Transmission & communication",
        domain="action",
        description="Traduire, enseigner, vulgariser, convaincre, animer un collectif.",
        status="SUPPORTED",
        typical_timescale="dispositional",
        role="capability",
        mappings=[dict(source="icf", source_iri="icf:d3", match="close")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("transmettre", "enseigner", "former", "vulgariser", "animer", "présenter",
                 "accompagner", "encadrer", "former", "sensibiliser", "expliquer", "convertir"),
    ),
    dict(
        id="act_adapt_improvise",
        label="Adaptabilité & improvisation",
        domain="action",
        description="Réponse efficace à l'imprévu, au changement de contexte et à l'incertitude.",
        status="SUPPORTED",
        typical_timescale="episodic",
        role="capability",
        mappings=[dict(source="icf", source_iri="icf:d2", match="related")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("adaptabilité", "improvisation", "imprévu", "flexibilité", "polyvalence",
                 "débrouillardise", "réactivité", "agilité", "replanifier", "rebondir"),
    ),
    dict(
        id="act_sustained_action",
        label="Persistence & exécution soutenue",
        domain="action",
        description="Tenir une action dans la durée, gérer la charge, éviter l'abandon.",
        status="SUPPORTED",
        typical_timescale="dispositional",
        role="capability",
        mappings=[dict(source="icf", source_iri="icf:d2", match="close")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("persévérance", "régularité", "tenue", "endurance mentale", "constance",
                 "assiduité", "discipline", "ne pas lâcher", "soutenue"),
    ),
    dict(
        id="act_leadership",
        label="Impulsion & conduite collective",
        domain="action",
        description="Entraîner, décider, assumer une responsabilité et une vision pour un collectif.",
        status="PROPOSED",
        typical_timescale="dispositional",
        role="capability",
        mappings=[dict(source="icf", source_iri="icf:d7", match="related")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("leadership", "autorité", "direction", "décisionnaire", "porteur", "entraîner",
                 "vision", "management", "encadrement", "équipe", "meneur"),
    ),

    # ------------------------------------------------------------------
    # DYNAMICS — how the human functions over time
    # ------------------------------------------------------------------
    dict(
        id="dyn_learning_rate",
        label="Vitesse d'apprentissage",
        domain="dynamics",
        description="Taux d'acquisition d'une nouvelle compétence ou d'une nouvelle connaissance.",
        status="SUPPORTED",
        typical_timescale="episodic",
        role="trait",
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:learning", match="close")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("apprend vite", "rapidité d'apprentissage", "courbe", "progrès", "facilité",
                 "tutorat", "formation", "assimile", "learning"),
    ),
    dict(
        id="dyn_retention",
        label="Rétention & oubli",
        domain="dynamics",
        description="Persistance d'une compétence ou d'une connaissance dans le temps (demi-vie, réactivation).",
        status="SUPPORTED",
        typical_timescale="episodic",
        role="trait",
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:memory_consolidation", match="close")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("oublier", "rétention", "demi-vie", "réactivation", "maintenir", "reprise",
                 "recyclage", "rester", "retention"),
    ),
    dict(
        id="dyn_transfer",
        label="Transfert inter-contextuel",
        domain="dynamics",
        description="Mobilisation d'une compétence acquise dans un contexte vers un autre (transfert, généralisation).",
        status="SUPPORTED",
        typical_timescale="dispositional",
        role="trait",
        mappings=[dict(source="cognitive_atlas", source_iri="cogatlas:transfer", match="related")],
        evidence_channels=("behavioral", "subjective"),
        aliases=("transfert", "transposable", "réutiliser", "généraliser", "ailleurs", "autre domaine",
                 "transversale", "bridge", "bridging", "transfer"),
    ),
    dict(
        id="dyn_cognitive_load",
        label="Charge cognitive & allostasis",
        domain="dynamics",
        description="Rapport entre la demande de la tâche et les ressources disponibles ; régulation de l'effort.",
        status="PROPOSED",
        typical_timescale="momentary",
        role="state_modulator",
        requires_context=("task", "environment"),
        mappings=[dict(source="icf", source_iri="icf:b1300", match="related")],
        modulators=("mental_attention", "mental_working_memory", "mental_cognitive_control"),
        aliases=("charge", "surcharge", "complexité", "multitâche", "allocation", "effort",
                 "cognitive load", "charge mentale"),
    ),
    dict(
        id="dyn_state_trait",
        label="État vs trait",
        domain="dynamics",
        description="Séparation entre dispositions stables (trait) et fluctuations transitoires (état) pour un même construit.",
        status="SUPPORTED",
        typical_timescale="dispositional",
        role="meta",
        mappings=[dict(source="icf", source_iri="icf:capacity_vs_performance", match="related")],
        evidence_channels=("behavioral", "subjective", "contextual"),
        aliases=("état", "trait", "stable", "variable", "circonstance", "moment"),
    ),
]


def _coerce(raw: list[dict]) -> list[Construct]:
    out: list[Construct] = []
    for r in raw:
        mappings = tuple(ExternalMapping(**m) for m in r.get("mappings", ()))
        r = dict(r)
        r["mappings"] = mappings
        out.append(Construct(**r))
    return out


CONSTRUCTS: list[Construct] = _coerce(_RAW)

BY_ID: dict[str, Construct] = {c.id: c for c in CONSTRUCTS}


def get_construct(construct_id: str) -> Construct:
    if construct_id not in BY_ID:
        raise KeyError(f"Unknown construct: {construct_id}")
    return BY_ID[construct_id]


def constructs_by_domain(domain: str) -> list[Construct]:
    if domain not in DOMAINS:
        raise ValueError(f"Unknown domain: {domain}")
    return [c for c in CONSTRUCTS if c.domain == domain]


def all_aliases() -> list[str]:
    """Flat list of surface markers (used by the lexical decoder)."""
    return [a for c in CONSTRUCTS for a in c.aliases if a]


# Registry of domain descriptors used by the UI / profile.
DOMAIN_META = {
    "physical": {
        "title": "Physique",
        "description": "Caractéristiques du corps — fonctions corporelles (ICF b*), sensori-motricité, énergie, santé.",
    },
    "mental": {
        "title": "Mental",
        "description": "Processus cognitifs & affectifs — perception, attention, mémoire, langage, contrôle, métacognition, émotion, motivation.",
    },
    "action": {
        "title": "Capacité d'action",
        "description": "Ce que la personne peut faire — savoir-faire, organisation, transmission, adaptation, impulsion.",
    },
    "dynamics": {
        "title": "Fonctionnement",
        "description": "Dynamique dans le temps — apprentissage, rétention/oubli, transfert, charge, état vs trait.",
    },
}


def domain_title(domain: str) -> str:
    return DOMAIN_META[domain]["title"]
