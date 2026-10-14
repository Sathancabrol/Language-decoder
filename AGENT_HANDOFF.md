# Agent handoff — Language-decoder

> **Règle :** tout agent qui commence ici doit lire ce fichier en premier, puis les instructions du dépôt et l'état réel du code. À la fin de chaque session, il met à jour ce fichier pour que le prochain agent reprenne sans repartir de zéro.

## État de passation

- **Dernière mise à jour du handoff :** 2026-10-11
- **Dernier audit de code complet :** non confirmé
- **État d'exécution / tests :** non vérifié dans cette passation
- **Projet :** Projet de décodage du langage — périmètre à confirmer
- **Priorité portefeuille :** P2
- **État :** initialisation du handoff; ne pas interpréter ce fichier comme la preuve qu'un audit a été exécuté.

## Résumé du dernier état connu

L'existence du dépôt a été vérifiée; le README a été consulté lorsqu'il était disponible. Le code, les tests et les previews n'ont pas été intégralement exécutés dans cette passation. Lire les audits et décisions existants avant de refaire du travail.

## Instruction au prochain agent

Commencer par déterminer l'objectif réel à partir des fichiers et de l'historique Git. Ne pas inventer de périmètre ni créer d'architecture avant d'avoir établi le besoin.

### Procédure obligatoire

1. Lire ce fichier, le README, les instructions locales (par exemple `AGENTS.md`, `CONTRIBUTING.md`) et les derniers audits/notes de décision disponibles.
2. Examiner le statut Git, les commits récents, les branches pertinentes, les PR/issues et les résultats CI accessibles.
3. Reconstituer ce qui est fait, en cours, bloqué, proposé et réellement vérifié. La présence de code ou de documentation ne prouve pas qu'une fonctionnalité fonctionne.
4. Identifier le besoin prioritaire à partir de la demande utilisateur la plus récente, des objectifs du projet, des dépendances et des preuves. Si le besoin est ambigu, faire un audit ciblé plutôt qu'une refonte arbitraire.
5. Faire une seule unité de travail utile et limitée. Préserver les modifications existantes; travailler sur une branche dédiée si une modification de code est nécessaire.
6. Exécuter les vérifications pertinentes et consigner les commandes, le commit testé et les résultats. Si rien n'a été exécuté, le dire explicitement.
7. Mettre à jour ce fichier avant de terminer : état, audit, tests, décisions, blocages et prochaine action. Ajouter une entrée au journal sans effacer les incertitudes précédentes.

## Prochaine action

- [ ] Lire les audits et décisions antérieurs.
- [ ] Établir l'état réel du code et des tests.
- [ ] Choisir et justifier la prochaine tâche prioritaire.
- [ ] Mettre à jour ce handoff avec preuves et résultats.

## Journal des sessions

### 2026-10-11 — Initialisation du handoff
- Ajout d'un point d'entrée commun pour les agents.
- Aucun audit complet ni test d'exécution n'est revendiqué.
- Prochaine étape : lire les documents du projet et produire un état vérifié.

## Format des mises à jour futures

À chaque session, ajouter : date; besoin traité; fichiers/branches/commits touchés; périmètre de l'audit; commandes de tests et résultats; décisions, sources et incertitudes; blocages/approbations; prochaine action et critère de réussite.

## Garde-fous

- Ne jamais inventer un résultat d'audit, un test réussi ou un état de déploiement.
- Ne pas supprimer ou écraser du travail existant sans comparaison et autorisation.
- Ne pas fusionner, déployer, publier, supprimer de branche ou engager une dépense sans autorisation explicite.
- Séparer les faits observés, les hypothèses et les recommandations.
- Pour la recherche externe, conserver URL, date, provenance et lien avec le besoin; respecter les licences et limites d'accès.
