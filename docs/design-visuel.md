# Langage visuel — aides Cognitorium

Les visuels du dépôt [COGNITORIUM](https://github.com/Sathancabrol/COGNITORIUM) (HUD verre, arbre-cerveau, graphe, radar, timeline de parcours, hub de connecteurs) et le PoC `learning/` (fond `#0b1020`, accent `#8db4ff`, cartes 18px) servent de **référence de forme**. Le proto clair (slate, pills, mode Essentiel / Expert) sert de **référence d’information**.

On copie la *grammaire*, pas le *théâtre de la certitude*.

## Ce qu’on retient

| Motif Cognitorium | Usage ici |
| --- | --- |
| Fond sombre, verre, lueur cyan | HUD du dashboard |
| Barre latérale de vues | Décodeur / Mémoire / Horizons / Principes |
| Kickers 11px, tracking large | Hiérarchie |
| Cartes 16–18px, bord `#263352` | Sections |
| Timeline de parcours (nœuds lumineux) | T1…Tn et journées 2040 |
| Graphe centré | Mémoire : relations projets / IA / concepts |
| Radar | **Couverture des langages** (modalités on/off), pas un score de personnalité |
| 4 KPI | Session Decoder et cartes 2040 |
| Avant → après | Horizons, pas des métriques individuelles |
| Hub de connecteurs | Sources GPT / Claude / Kimi / Arena / Anara |
| Learning loop | Observer → inférer → adapter → corriger |
| Mode Essentiel / Expert | L’essentiel est le décodeur ; l’expert est JSON + graphe |

## Ce qu’on refuse (même si les images le montrent)

- « Cognitive resilience 82 % » sans intervalle ni preuves.
- Jumeau numérique qui *mirror the mind*.
- « 1,8 M de nœuds » décoratif.
- Feux, débuffs, jauge de culpabilité (esthétique jeu / diagnostic).
- Auth ADN + rythme cardiaque comme feature.
- Camembert d’émotions.

Un radar plein à 85 % sur « raisonnement analytique » contredit `docs/incertitude.md`. Le radar du prototype se remplit seulement si la **modalité est collectée**, et reste vide sinon — portrait de la minimisation.

## Tokens

```
--bg: #070b15
--panel: #0b1020
--card: rgb(17 25 45 / 0.82)
--line: #263352
--ink: #edf2f7
--muted: #8ea2c9
--accent: #7dd3fc
--accent-2: #8db4ff
--measure: #2dd4bf
--infer: #e4b15a
```

Polices système uniquement (minimisation : pas de fonte distante). L’Inter des visuels Cognitorium n’est pas chargée.

## Vues du livrable (écho de la planche « 12 views »)

Les planches Cognitorium empilent skill tree, digital twin, knowledge graph, competence map, learning engine, etc. Pour Language Decoder on n’en garde que quatre, chacune avec une question :

1. **Décodeur** — que mesure-t-on, qu’estime-t-on, qu’adapte-t-on ?
2. **Mémoire** — d’où vient la connaissance, que peut-on coller dans une autre IA ?
3. **Horizons 2040** — que devient l’interface si le contexte change, et où sont les lignes rouges ?
4. **Principes** — HTML, incertitude, minimisation.

Le reste (arbre de compétences, ROME, posters) reste dans Cognitorium.
