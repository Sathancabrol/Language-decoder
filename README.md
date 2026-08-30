# Language Decoder

Prototype de dashboard pour **lire les langages de l’humain sans prétendre lire son intérieur**.

La science permet d’observer des signes (comportement, parole, physiologie, éventuellement BCI), de les relier au contexte et au temps, d’estimer des états latents **avec une incertitude affichée**, puis d’adapter une interface de façon **explicable, réversible et minimale**.

Les données affichées sont **simulées**. Ce n’est pas un diagnostic médical.

> Observer les signes, comprendre le contexte, représenter les états, anticiper les besoins et adapter l’interface.

## Ouvrir le prototype

Servir le dossier et ouvrir `index.html` :

```bash
python3 -m http.server 8080
```

Puis visiter `http://localhost:8080`.

Sans serveur, le script se rabat sur des données intégrées (le `fetch` du JSON peut échouer en `file://`).

## Contenu du dépôt

```
language-decoder/
├── README.md
├── index.html                 # dashboard
├── css/dashboard.css
├── js/dashboard.js
├── data/session-simulee.json  # contrat de données
└── docs/
    ├── discussion.md          # archive de la réflexion
    ├── conseils-appliques.md  # chaque conseil → un geste
    ├── format-html.md         # format HTML retenu
    ├── incertitude.md         # indicateurs visuels
    └── minimisation.md        # données minimales
```

Le dossier `docs/` conserve les remarques de la discussion. Le dashboard les applique.

## Trois réponses de cadrage

**Quel format HTML ?** HTML5 sémantique, `lang="fr"`, CSS et JS locaux, JSON à part, aucune dépendance distante. Pas de `<meter>` pour une hypothèse (cela simulerait une grandeur connue). Détail : [`docs/format-html.md`](docs/format-html.md).

**Quels indicateurs d’incertitude ?** Point + intervalle, hypothèses concurrentes non exclusives, hachures pour l’inféré / trait plein pour le mesuré, écart à la ligne de base, qualité de signal, bande temporelle, preuves citées, correction utilisateur. Pas de feu tricolore ni de camembert d’émotions. Détail : [`docs/incertitude.md`](docs/incertitude.md).

**Comment minimiser les données ?** Finalité unique (adapter l’interface pendant la tâche), features plutôt que brut, consentement par modalité, conservation = session, pas d’identité, EEG / audio / visage **éteints**, refus possible. Moins de signaux ⇒ intervalles plus larges, pas un silence trompeur. Détail : [`docs/minimisation.md`](docs/minimisation.md).

## Ce que le dashboard sépare

| Couche | Nature |
| --- | --- |
| Langages | Modalités on/off (minimisation) |
| Signaux | Mesures / caractéristiques |
| États | Hypothèses + intervalles |
| Temps | T1…Tn avec bande d’incertitude |
| Action | Suggestion d’interface, refus possible |
| Représentation | JSON données / hypothèses / décision |

## Suite (visualisation livrable)

Ce dépôt est conçu pour être repris :

1. Conserver `data/session-simulee.json` comme contrat.
2. Conserver `data-kind` (`measure` | `inference` | `action`) et les classes d’incertitude.
3. Brancher un jeu anonymisé, puis seulement des capteurs avec consentement.
4. Documenter le modèle d’inférence réel et ses seuils.

Principes à ne pas diluer : incertitude visible, minimisation, contrôle humain, pas de diagnostic.
