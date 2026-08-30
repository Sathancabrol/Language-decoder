# Cognitorium — Representation Engine

**Outil de visualisation temps réel.** Pas le générateur de code.

Cognitorium, dans l’idée finale, n’est pas « une appli avec un graphe ». C’est un **moteur de représentation multimodale** : une même information a plusieurs projections coordonnées. Ce dépôt produit **uniquement** l’instrument qui affiche les données en direct.

```
INFORMATION → structure → encodage → projection → VUES COORDONNÉES
```

Les données sont **simulées**. Ce n’est pas un diagnostic, pas un jumeau mental, pas un outil d’auth.

## Lancer

```bash
python3 -m http.server 8080
```

Ouvrir `http://localhost:8080`. Espace = lecture / pause.

## Ce que l’instrument montre (toujours les mêmes données)

| Vue | Question |
| --- | --- |
| Graphe **K / E / I** | Science ≠ mesure ≠ inférence (HCSM) |
| Oscillogrammes | Features live (pas de brut ECG) |
| Fan chart | Temps + incertitude |
| Inspecteur | `ConstructEstimate` (valeur, intervalle, preuves, alternatives, refus) |
| Carte des signes | D’où vient le langage, pas un avatar de l’âme |
| Langages on/off | Minimisation : moins de preuves → intervalle plus large ou `Refusal` |

Cliquer un nœud **lie** toutes les vues. Couches K, E, I dans le rail : masquer sans détruire.

## Périmètre

| Dans cet outil | Plus tard (autre outil) |
| --- | --- |
| Affichage live | Génération de code |
| Vues coordonnées | Distilleur d’expériences |
| Incertitude, provenance, refus | Connecteurs GPT / Claude / capteurs réels |
| | ROME, skill tree carrière, learning engine |

Voir [`docs/outil-visualisation.md`](docs/outil-visualisation.md).

## Principes conservés

- Inférence probabiliste, jamais lecture intérieure
- Point + intervalle, hypothèses concurrentes
- Minimisation par modalité
- HTML5 local, sans CDN

Notes et mémoire : [`docs/`](docs/).
