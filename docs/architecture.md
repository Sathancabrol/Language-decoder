# Architecture — Language-decoder v0.1

## Positionnement

Language-decoder n'est ni Cognitorium ni HCSM. Il est le **décodeur** qui
transforme des observations en modèle d'humain, et le **pont** entre les
données brutes et l'interface.

```text
  reaserch-engine  (recherche, claims, preuves, suffisance)
  HCSM             (état cognitif : inférence, refus, incertitude, provenance)
  Cognitorium      (capital cognitif : métier → mission → compétence → capacité)
        │
        └── Language-decoder  ←  "le langage = l'humain"
              physique · mental · capacité d'action · fonctionnement
        │
        └── Interface (UI)  ← "connecter avec un interface utilisateur"
```

## Couches

```text
┌───────────────────────────────────────────────────────────────┐
│   INTERFACE (ui/) : index.html, styles.css, app.js            │
│   lit DecodedHuman.json ; POST /api/decode                    │
└──────────────────────────────┬────────────────────────────────┘
                               ↓
┌───────────────────────────────────────────────────────────────┐
│   profile.py  — DecodedHuman (contrat UI) + orchestration     │
└───────────────┬──────────────────────────────┬────────────────┘
                ↓                              ↓
┌───────────────────────────────┐   ┌───────────────────────────┐
│  functioning.py (ICF)         │   │  dynamics.py (temps)      │
│  capacity ⊥ perf ⊥ particip.  │   │  oubli/réactiv./transfert │
└───────────────┬───────────────┘   └───────────┬───────────────┘
                ↓                              ↓
┌───────────────────────────────────────────────────────────────┐
│  inference.py — ConstructEstimate | Refusal                   │
│  admissibilité · fusion par canal · incertitude · alternatives│
└──────────────────────────────┬────────────────────────────────┘
                               ↓
┌───────────────────────────────────────────────────────────────┐
│  decoder.py — observations (lexical / items / IA guardée)     │
│  evidence.py — Observation, provenance, canal, fenêtre        │
│  ontology.py — construits, alignements, épistémique           │
└───────────────────────────────────────────────────────────────┘
```

## Contrat d'estimation

Pour un construit `c`, le moteur renvoie **soit** un `ConstructEstimate`
(valeur 0..1, incertitude décomposée, alternatives nommées), **soit** un
`Refusal(code, message)`. Il ne produit jamais de valeur par défaut.

`ConstructEstimate ≠ Capacité ≠ État ≠ Performance` : la projection de
fonctionnement est toujours `HYPOTHESIS`.

## Frontière d'interface

- HCSM fournit `CognitiveState` + `FunctionalProjection?` + `Refusal*`.
- Language-decoder relie à des compétences, expériences, parcours (Cognitorium).
- L'interface **n'écrit pas** dans le graphe d'inférence.
- Aucune décision scolaire / médicale / managériale n'est justifiée par un score.

## Décisions de conception

1. **Noyau déterministe et hors-ligne** (stdlib Python uniquement) → reproductible,
   auditable partout.
2. **Alignement externe obligatoire** (exact/close) pour tout construit ; `none`
   = stockable mais non estimable.
3. **Admissibilité par filtre** : contexte/fenêtre exigés seulement pour les
   *state modulators* (capacité ≠ état).
4. **Fusion non additive** : même canal → renforcement ; canaux différents →
   confrontation (convergence bonus, divergence pénalité). Le nombre d'items
   n'est pas une confiance.
5. **IA gardée** : `decode_ai_json` plafonne à niveau 4, rétrograde `exact` →
   `close`, cap de confiance.
6. **Garde-fou épistémique** : L5 (conclusion psychologique) jamais produit.

## Schémas

`language_decoder/schemas/decoded-human.schema.json` formalise le contrat
interface (observations, refus, projections, résumé épistémique).

## Sécurité / gouvernance (à venir)

isolation de secrets, périmètre outils, gestion de contenu non fiable,
préservation de provenance, minimisation de données, approbation humaine pour
les actions à fort impact.
