# Language-decoder

**Moteur de décodage de l'humain.** De la langue naturelle (récit, CV, entretien,
mesure, questionnaire) vers un **profil humain décodé**, auditable et prêt pour
l'interface — qui couvre **ce que l'humain est et ce qu'il peut faire** :

| Volet | Signification | Référentiel |
|---|---|---|
| **Physique** | Caractéristiques du corps, sensori-motricité, énergie, santé | ICF fonctions corporelles (`b*`) |
| **Mental** | Perception, attention, mémoire, langage, raisonnement, contrôle exécutif, métacognition, émotion, motivation, cognition sociale | RDoC · Cognitive Atlas · psychologie cognitive |
| **Capacité d'action** | Ce que la personne *peut faire* : savoir-faire, organisation, transmission, adaptation, impulsion | ICF activités (`d*`) · CAPABILITY |
| **Fonctionnement** | Comment l'humain fonctionne *dans le temps* : état vs trait, oubli, réactivation, transfert, charge | Ebbinghaus · loi de puissance de la pratique · transfert |

> Le "langage" décodé n'est pas une langue naturelle : c'est **l'humain**. Ce
> dépôt transforme des observations en un modèle d'humain structuré, puis le
> branche sur une interface.

## Principes (épreuvés par la littérature)

- **Évidence d'abord, jamais un score nu.** Chaque observation porte provenance,
  canal, alignement, qualité, fenêtre et niveau épistémique.
- **Ontologie externe plutôt qu'inventée.** Alignements `exact`/`close` vers
  Cognitive Atlas, RDoC, ICF, HPO — réutilisés depuis l'ontologie HCSM.
- **Refus plutôt que valeur par défaut.** Un construit non estimable émet un
  `Refusal(code, message)` formel. Pas de score silencieux.
- **Capacité ≠ état ≠ performance.** Séparation stricte (ICF) ; une projection
  de fonctionnement est toujours une **hypothèse**, jamais une déduction.
- **Incertitude décomposée** (mesure / évidence / inférence) et **alternatives
  nommées**, jamais éliminées en silence.
- **Niveau épistémique 1→5** : fait → compétence → capacité → hypothèse →
  **conclusion psychologique (jamais produite automatiquement)**.
- **Noyau déterministe** (stdlib Python) ; adaptateur IA *plafonné* et gardé.

## Pipeline

```text
texte / items / IA-JSON
   → DECODER      (Observations alignées, provenancées)
   → INFERENCE    (ConstructEstimate | Refusal, incertitude, alternatives)
   → FUNCTIONING  (projections ICF, HYPOTHESIS)
   → DYNAMICS     (rétention / réactivation / transfert)
   → DecodedHuman (contrat interface, JSON-safe)
```

## Installation & usage

```bash
# Python 3.10+ (aucune dépendance obligatoire ; pytest pour les tests)
python -m language_decoder.cli decode --input profil.txt --title "Nom" --person h-001
#     écrit ui/data/profile.json et affiche un résumé

# Interface (livre en local, preview navigateur)
python -m language_decoder serve --port 9000
#     http://0.0.0.0:9000
```

Tests :

```bash
python -m pytest tests/ -q
```

## Structure

```text
language_decoder/
  ontology.py        # graphe de connaissance : construits, alignements, épistémique
  evidence.py        # Observation, provenance, fenêtre, canal, qualité
  inference.py       # moteur : admissibilité, refus, fusion, incertitude, alternatives
  decoder.py         # langue → observations (lexical + items + IA gardé)
  dynamics.py        # oubli, réactivation, transfert, état/trait, trajectoire
  functioning.py     # projections ICF (hypothèses)
  profile.py         # orchestrateur → DecodedHuman (contrat UI)
  cli.py / serve.py  # CLI + serveur statique/API
  schemas/           # contrats JSON-schema
ui/                  # interface (index.html, styles.css, app.js, data/profile.json)
tests/               # tests du moteur
docs/                # architecture et fondements littéraires
```

## Utilisation du moteur en Python

```python
from language_decoder import decode_human

profile = decode_human(
    text="Ingénieur de recherche, très forte capacité d'analyse …",
    person_id="h-bench",
    current_year=2026,
)
print(profile.to_json(indent=2))
```

## Fondements (résumé)

- **Ontologie des construits & alignements** : HCSM v0.1.0 (Cognitive Atlas,
  RDoC, ICF, HPO).
- **Séparation capacité/état/perf** : ICF (WHO, 2001) ; HCSM functioning model.
- **Cognition** : psychologie cognitive — processus (perception, attention,
  mémoire, langage, raisonnement, décision, métacognition, émotion, cognition
  sociale) d'après la taxonomie Cognitorium / état-de-l'art.
- **Dynamique** : courbe d'oubli (Ebbinghaus, 1885) ; loi de puissance de la
  pratique (Newell & Rosenbloom, 1981) ; transfert (Thorndike & Woodworth,
  1901) ; état/trait (HCSM CapacityProfile).
- **Rigueur** : CRONBACH & MEEHL (1955) validité de construit ; RDoC ;
  provenance FAIR / PROV-O.

Voir `docs/architecture.md` et `docs/fondements.md` pour le détail.
