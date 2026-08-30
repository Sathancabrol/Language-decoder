# Minimisation des données

Réponse à : *« Comment appliquer le principe de minimisation des données ici ? »*

La minimisation n’est pas un paragraphe juridique en bas de page. C’est une **architecture** : on ne collecte que ce qui sert la finalité, on n’extrait que des caractéristiques, on ne conserve pas, on laisse refuser.

Le prototype n’envoie rien : données simulées, pas de serveur de télémétrie, pas de cookie, pas de fonte distante.

## Finalité unique

Adapter l’interface **pendant** une tâche de résolution de problème (rythme, densité, aide proposée).  
Hors finalité : diagnostic, recrutement, notation, surveillance, inférence émotionnelle commerciale.

Une décision à fort impact n’est jamais automatique.

## Ce qui est collecté / ce qui ne l’est pas

| Langage | Collecté dans le cas d’étude | Raison |
| --- | --- | --- |
| Caractéristiques cardiaques (FC, HRV relative) | Oui, simulé | Écart à la ligne de base, utile à la charge / activation |
| Comportement de tâche (durée, erreurs) | Oui | Déjà produit par l’interface, faible sensibilité |
| Respiration | Non | Non nécessaire ici |
| EEG / BCI | Non | Très sensible, hors finalité |
| Audio de parole | Non | Identifiant, hors finalité |
| Vidéo / visage | Non | Biométrie forte, écartée |
| Identité nominale | Non | Profil `sim-001` anonyme |
| Tracé brut ECG / EEG | Non | Une feature suffit ; le brut n’est pas conservé |

L’utilisateur peut **désactiver** une modalité dans le dashboard. Le modèle continue avec plus d’incertitude au lieu d’exiger le signal.

## Règles opérationnelles

1. **Feature plutôt que brut.** 92 bpm, pas le waveform. « ↓ relative » pour la HRV, pas la série RR.
2. **Consentement par modalité**, pas un paquet unique « capteurs on ».
3. **Justification affichée** à côté de chaque langage (`pourquoi on le prend` / `pourquoi on le refuse`).
4. **Conservation = session.** Aucun `localStorage` des signaux. Un rechargement repart de la simulation.
5. **Pas de profil durable.** Pas d’historique multi-jours dans ce prototype.
6. **Ligne de base locale** (repos 68 bpm simulé), non partagée.
7. **Correction et refus** : l’utilisateur invalide une hypothèse ; l’adaptation d’interface se refuse.
8. **Pas de tiers.** CSS et JS locaux.
9. **Simulation visible.** Badge permanent « données simulées » pour qu’on ne confonde pas avec une mesure réelle.
10. **Droits rappelés** : accès à la représentation, correction, désactivation, absence de conservation.

## Alignement CNIL (documentation minimale)

À garder dans le livrable, même simulé :

- **Collecte** : modalités listées, base (simulation / plus tard consentement).
- **Sécurité** : pas de transit ; plus tard, chiffrement et séparation du brut.
- **Profils** : anonyme, pas de catégorie sensible inférée comme fait.
- **Durée** : session.
- **Droits** : correction, refus de modalité, non-prise de décision automatique.

Ce n’est pas un dossier d’analyse d’impact. C’est la trace que le design a intégré ces questions **avant** les capteurs réels.

## Conséquence visible sur l’incertitude

Minimiser n’est pas appauvrir en silence. Si le cardio est refusé, il reste le comportement de tâche : les intervalles s’élargissent, la confiance globale baisse, l’hypothèse « effort physique » s’effondre, « données insuffisantes » monte. Le système **dit** qu’il sait moins.

C’est le contrat : moins de données personnelles, plus d’humilité du modèle, contrôle conservé.

## Plus tard, capteurs réels

- Consentement explicite, séparé, révocable.
- Collecte sur l’appareil si possible.
- Destruction du brut après extraction.
- Interdiction d’entraîner un modèle secondaire sans nouvelle finalité.
- Aucune inférence émotionnelle présentée comme un fait.
