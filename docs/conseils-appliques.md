# Conseils appliqués dans le prototype

Chaque remarque de la discussion est reliée à un geste concret. Rien n’est laissé « pour plus tard » lorsqu’un affichage suffit.

| Conseil | Où c’est appliqué |
| --- | --- |
| Pensée systémique, pas une fiche unique | Pipeline à 5 + 8 étapes, langages multiples, relations mesure → hypothèse → action |
| Distinguer théorie et usage | Mesures à gauche, inférences hachurées, action d’interface à part |
| Compatibilité plutôt que classement | Pas de « vous êtes X » ; hypothèses concurrentes + correction |
| Cinq couches (individu, cognition, compétences, monde, parcours) | Conservées dans `discussion.md` ; ce dépôt traite la couche langages / cognition / interface |
| Observer → langages → signaux → features → contexte → état → temps → interface | Stepper + sections homonymes |
| Inférence probabiliste, pas lecture intérieure | Intervalles, alternatives, libellé « estimé » |
| Signal isolé ≠ émotion | Liste d’interprétations possibles du BPM ; cardio seul ne suffit pas |
| Ligne de base individuelle | 92 bpm affiché contre 68 bpm de repos |
| Représentation JSON (données / hypothèses / décision) | Carte « Représentation » et `data/session-simulee.json` |
| Métaphore de la langue, avec réserve | Titre « langages de l’humain » + note « pas une langue au sens strict » |
| Interface adaptative explicable et réversible | Action + déclencheurs + Accepter / Autre / Ignorer |
| Incertitude visible | Pistes point+intervalle, bande temporelle, qualité de signal — `docs/incertitude.md` |
| Minimisation | Modalités off par défaut sauf 2 ; pas de brut ; session — `docs/minimisation.md` |
| HTML sémantique sans dépendance | `docs/format-html.md`, fichiers locaux |
| CNIL : collecte, conservation, droits | Carte minimisation + checkboxes de consentement |
| Données simulées | Badge permanent, `meta.type: simulation` |
| Pas un diagnostic médical | Pied de page et `diagnostic_medical: false` |
| Pas de décision automatique à fort impact | `automatique_fort_impact: false` ; l’aide est proposée |
| L’utilisateur corrige | Correspond / Ne correspond pas / Je ne sais pas |
| BCI / ECG cités comme chaîne, pas branchés | Modalités présentes et **désactivées** |
| Cognition incarnée | Contexte (bureau, individuel) à côté des signaux du corps |
| Badge simulation + limites | En-tête et pied |
| Réemploi visualisation livrable | JSON contrat, `data-kind`, CSS d’incertitude stables |
| Conversation ≠ mémoire | `docs/conversations/` vs `docs/memoire/` + `data/memoire.json` |
| Continuer avec une IA | Vue Mémoire, bouton copier le contexte |
| Provenance | Chaque conversation : IA, date, projet, fichier |
| Memory + RAG + Graph, V1 seulement | Extraire à la main, graphe listé, pas d’embeddings encore |
| Format 2040 (persona, journée, 4 KPI, avant/après) | Vue Horizons, `data/monde-2040.json` |
| 2040 = scénarios | Badge / kicker « scénario », pas des mesures Decoder |
| L’humain décide l’éthique (Sarah 14:00) | Action d’interface réversible + lecture des cartes 2040 |
| Caméras urbaines / auth cardiaque | Lignes rouges dans Horizons (cyber, villes) |
| HUD Cognitorium | Sidebar, verre, teal, radar de couverture — `docs/design-visuel.md` |
| Refus des scores de traits à 82 % | Radar = modalités on/off, jamais « résilience cognitive » |

## Ce que le prototype refuse volontairement

- Camembert d’émotions.
- Feu tricolore.
- Une unique « émotion détectée ».
- Stockage `localStorage` des signaux.
- Scripts ou polices distants.
- Animation d’alarme.
