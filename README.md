# Language Decoder

Prototype HUD pour **lire les langages de l’humain sans prétendre lire son intérieur**.

Couche langages / interface de [Cognitorium](https://github.com/Sathancabrol/COGNITORIUM) : observer des signes, les relier au contexte et au temps, estimer des états **avec incertitude**, adapter l’interface — explicable, réversible, minimale.

Quatre vues :

1. **Décodeur** — mesures, hypothèses, action
2. **Mémoire** — conversations ≠ extraits, contexte à coller dans une autre IA
3. **Horizons 2040** — sept scénarios pour tester les lignes rouges
4. **Principes** — HTML, incertitude, minimisation

Les données sont **simulées**. Ce n’est pas un diagnostic médical.

> Observer les signes, comprendre le contexte, représenter les états, anticiper les besoins et adapter l’interface.

## Ouvrir

```bash
python3 -m http.server 8080
```

Puis `http://localhost:8080`. Ancres : `#decoder` `#memoire` `#horizons` `#principes`.

## Dépôt

```
├── index.html
├── css/dashboard.css          # HUD Cognitorium (teal / verre / sidebar)
├── js/dashboard.js
├── data/
│   ├── session-simulee.json   # contrat décodeur
│   ├── memoire.json           # décisions / idées / questions
│   └── monde-2040.json        # 7 domaines, lecture Decoder
└── docs/
    ├── conversations/         # journaux bruts (jamais écrasés)
    ├── memoire/               # extraits
    ├── design-visuel.md       # ce qu'on prend / refuse des visuels Cognitorium
    ├── discussion.md
    ├── format-html.md
    ├── incertitude.md
    └── minimisation.md
```

## Cadrage

**HTML** — sémantique, local, JSON à part. Pas de `<meter>` pour une hypothèse. [`docs/format-html.md`](docs/format-html.md)

**Incertitude** — point + intervalle, hypothèses concurrentes, hachure = inféré. Pas de feu tricolore, pas de « résilience 82 % ». [`docs/incertitude.md`](docs/incertitude.md)

**Minimisation** — features de session, EEG / audio / visage off, pas d’auth biométrique. Moins de signaux → intervalles plus larges. [`docs/minimisation.md`](docs/minimisation.md)

**Mémoire multi-IA** — centraliser le *contexte*, pas seulement les fichiers. V1 de ce dépôt : originaux + extraits + bouton « Continuer avec une IA ». [`docs/conversations/2026-08-30-memoire-multi-ia.md`](docs/conversations/2026-08-30-memoire-multi-ia.md)

**Visuels Cognitorium** — HUD, sidebar, radar de *couverture* (modalités collectées), 4 KPI, timeline, graphe. On refuse le jumeau qui lit l’esprit. [`docs/design-visuel.md`](docs/design-visuel.md)

## Suite livrable

Conserver le JSON, les `data-kind`, les classes d’incertitude, la séparation conversation / mémoire. Ne pas diluer : incertitude, minimisation, contrôle humain, pas de diagnostic.
