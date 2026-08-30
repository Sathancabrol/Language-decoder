# Outil de visualisation (périmètre actuel)

Cognitorium se scinde en deux outils. **Celui-ci est le premier.**

| Outil | Rôle | Statut |
| --- | --- | --- |
| **Representation Engine** | Afficher nos données en temps réel, en vues coordonnées | Ce dépôt, `index.html` |
| Générateur de code / distilleur | Produire, extraire, brancher des sources | Hors périmètre pour l’instant |

## Idée finale, réduite à l’affichage

Pas « une appli avec un graphe ». Un **moteur de représentation multimodale** :

```
INFORMATION → structure → tâche → encodage → projection → interaction → VUES COORDONNÉES
```

Une même observation (FC, erreur, temps) a plusieurs projections valides. Le choix n’est pas « quel graphique » mais « quelle représentation pour cette tâche, maintenant ».

## Ce que l’instrument montre

Toujours les mêmes données, liées (brushing) :

| Vue | Dimension | Tâche |
| --- | --- | --- |
| Graphe K / E / I | relationnelle | ne pas confondre science, mesure, inférence |
| Timeline + fan chart | 4D (temps) | évolution et incertitude |
| Oscillogrammes | 1D signaux | preuve brute (features, pas waveform ECG) |
| Radar de couverture | minimisation | ce qui est collecté, pas un profil de traits |
| Carte des langages | spatiale du corps | d’où vient le signe, pas un jumeau mental |
| Inspecteur | 0D + provenance | `ConstructEstimate` HCSM |

## Ce qu’il ne montre pas

- Génération de code
- ROME / métiers / skill tree de carrière
- Learning engine
- Atlas 2050 / 1,8 M de nœuds
- Score unique de personnalité

## Temps réel

Horloge `T0`, lecture / pause, curseur sur l’historique. Les capteurs sont **simulés**. Un canal éteint élargit les intervalles ou produit un `Refusal` (`NO_EVIDENCE`) — le modèle refuse plutôt que d’inventer.
