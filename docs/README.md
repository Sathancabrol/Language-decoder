# Docs — mémoire du projet

Deux couches, volontairement séparées :

| Couche | Dossier | Rôle |
| --- | --- | --- |
| **Conversation** (journal brut) | [`conversations/`](conversations/) | Originaux, provenance, date, IA |
| **Mémoire** (extrait) | [`memoire/`](memoire/) + `data/memoire.json` | Décisions, idées, questions, versions |

Les originaux ne sont jamais remplacés par la synthèse.

## Conversations archivées

| Fichier | Sujet |
| --- | --- |
| [2026-08-30-prise-de-notes.md](conversations/2026-08-30-prise-de-notes.md) | Page manuscrite, cinq couches, chaîne langages → interface |
| [2026-08-30-memoire-multi-ia.md](conversations/2026-08-30-memoire-multi-ia.md) | Centraliser GPT/Claude/Kimi/Arena/Anara, PAM, RAG+graphe |
| [2026-08-30-monde-2040.md](conversations/2026-08-30-monde-2040.md) | Sept domaines 2040, lecture Decoder (lignes rouges) |

## Cadrage du prototype

| Fichier | Contenu |
| --- | --- |
| [discussion.md](discussion.md) | Synthèse Language Decoder (chaîne à 8 étapes) |
| [conseils-appliques.md](conseils-appliques.md) | Conseil → geste |
| [format-html.md](format-html.md) | Format HTML |
| [incertitude.md](incertitude.md) | Indicateurs d’incertitude |
| [minimisation.md](minimisation.md) | Données minimales |
| [design-visuel.md](design-visuel.md) | Grammaire HUD Cognitorium, sans fausse précision |

Machine-readable : `data/session-simulee.json`, `data/memoire.json`, `data/monde-2040.json`, `data/ontology.json`.

L’instrument live : [`outil-visualisation.md`](outil-visualisation.md).  
Chrome issu des illustrations : [`illustrations.md`](illustrations.md).  
HUD K·E·I : [`hud.md`](hud.md) · [`hud-hcsm-kei.jpg`](hud-hcsm-kei.jpg).
