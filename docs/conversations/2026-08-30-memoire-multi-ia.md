# Conversation — mémoire multi-IA

| Champ | Valeur |
| --- | --- |
| Id | `c-pam-2026-08-30` |
| Date | 30 août 2026 |
| IA | Claude (et relais) |
| Projet | Personal AI Memory |
| Type | journal brut condensé |

Ceci est le **journal**. La synthèse exploitable est dans `docs/memoire/` et `data/memoire.json`.

## Demande

Notes et fichiers éparpillés (GPT, Claude, Anara, Arena, Kimi…). Comment centraliser ? Une discussion avec un chat devrait laisser une trace — une mémoire multi-chat.

## Réponse (condensée)

Ce n’est pas un dossier de notes. C’est une **mémoire persistante multi-IA** : chaque conversation devient une source exploitable par les autres.

### 4 couches

```
GPT, Claude, Kimi, Arena, Anara, fichiers/PDF/web
        → MÉMOIRE CENTRALE
            projets, idées, décisions, notes, sources, conversations, fichiers
        → recherche sémantique
        → nouveau chat / nouvelle IA
```

Centraliser le **contexte**, pas seulement les fichiers. Chaque élément garde sa **provenance**.

### Conversation ≠ mémoire

- **Conversation** : historique brut, jamais perdu.
- **Mémoire** : connaissance extraite (décision, hypothèse, idée, question), versionnée.

Une IA doit pouvoir dire : « proposée par Kimi le 27, modifiée après Claude le 29 ».

### MVP à 5 fonctions

1. Importer une conversation (md, txt, json ChatGPT).
2. Importer un fichier (PDF, DOCX, image…).
3. Créer une discussion-projet et y rattacher des sources.
4. Recherche globale (pas seulement les titres).
5. **Continuer avec une IA** : générer un contexte (projet, décisions, questions ouvertes, dernière conversation) à coller.

Ne pas commencer par une usine à gaz. Plus tard : PostgreSQL + pgvector + graphe, connecteurs.

### Méthodes les plus utiles ici

| Méthode | Rôle | Suffisant seul ? |
| --- | --- | --- |
| Second brain (PARA, Zettelkasten, CODE) | Organisation | Non |
| RAG / base documentaire | Retrouver les passages | Cœur du V1 |
| Mémoire structurée | Décisions / idées machine-readable | V2 |
| Knowledge graph | Relations, versions, provenance | V3 |
| Memory + RAG + Graph | Combinaison retenue | Oui, progressive |

**Conversation as a first-class object** : id, IA, projet, date, sujets, décisions, idées, sources, relations (suite de #173, contredit idée #42).

Les IA actuelles ont chacune une mémoire A/B/C. L’objectif : **une mémoire externe**, les modèles n’étant que des interfaces.

Noms possibles : Personal AI Memory (PAM), AI Knowledge Hub, External Cognitive Memory.

### Versions

- V1 : conversations + fichiers + recherche + projets
- V2 : extraction idées / décisions / questions / sources
- V3 : graphe + versions + relations
- V4 : GPT / Claude / Kimi / Anara / Arena → la même mémoire

Ce dépôt Language Decoder joue déjà le V1/V2 pour **ce** fil : originaux dans `docs/conversations/`, extraits dans `data/memoire.json`.
