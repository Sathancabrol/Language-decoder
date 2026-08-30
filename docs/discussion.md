# Language Decoder — Discussion et réflexion

Archive des remarques issues de l’analyse de la prise de notes manuscrite et de la conversation sur le langage de l’humain et son interface. Ce fichier conserve le fond. L’application concrète se trouve dans le prototype (`index.html`) et dans `docs/conseils-appliques.md`.

---

## Lecture générale de la prise de notes

La page n’est pas un texte linéaire : mots-clés, flèches, embranchements, exemples et relations. Le centre de gravité relie cognition, compétences, métiers et formation — fondements proches de Cognitorium — tout en ouvrant, sur la droite, une chaîne distincte : **science → langages de l’objet → représentation → interface**.

C’est cette seconde chaîne qui constitue Language Decoder.

### Structure visible de la note

- **Haut gauche** : titre ou question générale, schéma en arborescence.
- **Centre** : cognition, apprentissage, orientation.
- **Bas gauche** : chaîne compétences → activités → formations → métiers.
- **Droite** : la science permet de mieux comprendre son environnement ; exemple « comprendre l’humain » donc **comprendre ses langages** (biomarqueurs, BPM, signaux BCI) ; inférer des états à un instant T ; avec une base temporelle T1, T2… prévoir selon le contexte ; **se représenter** l’objet comme on apprend une langue ; **appliquer le savoir et créer l’interface**.

L’organisation passe d’une liste d’informations à un **modèle relationnel**.

---

## Partie Cognitorium (contexte, non le cœur de ce dépôt)

Le métier n’est pas une réponse unique, mais le résultat d’une mise en relation :

caractéristiques individuelles → processus cognitifs → compétences → activités → formations → contextes de travail → trajectoires.

Cinq couches à ne pas confondre :

| Couche | Question centrale |
| --- | --- |
| Individu | Qui est la personne ? |
| Cognition | Comment apprend-elle, raisonne-t-elle et agit-elle ? |
| Compétences | Que sait-elle déjà faire ? |
| Monde professionnel | Quelles activités et quels métiers existent ? |
| Parcours | Comment passer d’une situation à une autre ? |

Architecture fonctionnelle associée : explorer son profil ; identifier ses compétences ; explorer les activités ; comparer les environnements ; construire un parcours.

Language Decoder se place surtout sur la couche **cognition / langages / interface**. Il pourra plus tard alimenter une visualisation livrable de Cognitorium.

---

## Idée centrale de Language Decoder

La science permet de mieux comprendre un objet dans son environnement. Lorsque l’objet est l’humain, il faut identifier ses **langages** : parole, gestes, comportements, signaux physiologiques, éventuellement signaux neurophysiologiques.

Un signal n’a pas une signification unique. Il s’interprète avec le **contexte**, la **ligne de base individuelle** et l’**évolution dans le temps**. Le système ne lit pas une émotion : il produit une **hypothèse probabiliste** sur un état latent.

Formulation de la discussion :

> La science permet de comprendre les langages d’un objet. Lorsqu’il s’agit de l’humain, ces langages sont constitués de comportements, de paroles, de signaux physiologiques et éventuellement de signaux cérébraux. En les observant dans le temps et dans leur contexte, on peut estimer certains états, formuler des hypothèses et concevoir une interface adaptée.

Condition : parler d’**inférence probabiliste**, jamais de lecture directe de l’état intérieur.

---

## Chaîne en huit étapes

1. **Observer l’objet** — l’être humain dans son environnement.
2. **Identifier ses langages** — parole, écriture, gestes, expressions, rythme cardiaque, respiration, activité cérébrale, interactions numériques.
3. **Mesurer les signaux** — ECG ou fréquence cardiaque, HRV, conductance cutanée, respiration, EEG / BCI, actions dans l’interface.
4. **Extraire des caractéristiques** — rythme, amplitude, fréquence, variation, synchronisation, évolution temporelle. Pas le signal brut si une feature suffit.
5. **Relier au contexte** — tâche, événement, environnement, charge, interaction sociale, fatigue.
6. **Estimer un état latent** — activation, stress possible, engagement, charge cognitive, fatigue, valence — toujours avec une confiance.
7. **Modéliser l’évolution** — T1, T2, T3… tendance ou probabilité future.
8. **Concevoir l’interface** — adapter l’information, le rythme, la difficulté ou le feedback, sans retirer le contrôle.

Chaîne courte retenue comme principe fondateur :

> Observer les signes, comprendre le contexte, représenter les états, anticiper les besoins et adapter l’interface.

---

## Exemple cardiaque

```
Signal cardiaque
→ fréquence et variabilité des battements
→ comparaison avec le niveau habituel de la personne
→ prise en compte du contexte
→ estimation d’un état d’activation
→ adaptation de l’interface
```

Une fréquence élevée peut correspondre à un effort, une excitation, un stress, une peur, une douleur ou un déplacement. Elle ne signifie pas « émotion négative ».

Formulation rigoureuse :

> À partir de plusieurs signaux et du contexte, le système estime la probabilité de certains états de l’utilisateur.

À éviter :

> Le système déduit directement l’émotion de l’utilisateur.

Les revues scientifiques soulignent l’ambiguïté de l’inférence émotionnelle à partir du seul rythme cardiaque : les mêmes réponses physiologiques peuvent correspondre à des émotions différentes. Un signal isolé suffit rarement.

---

## Métaphore de la langue

| Langue humaine | Système de compréhension |
| --- | --- |
| Signes ou sons | Signaux corporels, cérébraux et comportementaux |
| Grammaire | Relations entre les signaux et le contexte |
| Sens | État ou intention **estimée** |
| Dialogue | Interaction humain–interface |
| Réponse adaptée | Feedback ou action du système |

Les biomarqueurs **ne sont pas une langue au sens strict**. Un mot a une signification conventionnelle ; un signal physiologique est ambigu, continu et dépendant du contexte. On parle plutôt de **langage multimodal de l’humain** ou de **système de signes incarnés**.

Après l’observation : **se représenter** l’objet (construire un modèle), puis appliquer le savoir (interface).

---

## Modèle de représentation

Une observation distingue données, hypothèses et décision :

```json
{
  "temps": "T2",
  "contexte": "résolution d'un problème",
  "signaux": {
    "frequence_cardiaque": "élevée",
    "variabilite_cardiaque": "diminuée",
    "temps_sur_tache": "long"
  },
  "hypotheses": [
    { "etat": "charge cognitive élevée", "confiance": 0.68 },
    { "etat": "frustration possible", "confiance": 0.42 }
  ],
  "action_interface": "proposer une aide progressive"
}
```

Le modèle peut aussi porter : état, contexte, signaux, hypothèses, **niveau de confiance**, évolution, action possible.

---

## Interface adaptative

Comprendre les signaux permet d’adapter l’interface à l’état et au contexte, par exemple :

- ralentir le rythme si une surcharge cognitive est probable ;
- proposer une autre explication après plusieurs erreurs ;
- fractionner une tâche complexe ;
- modifier la difficulté ;
- demander une confirmation ;
- afficher **pourquoi** une adaptation a été déclenchée.

L’humain est un système intégré : cerveau, corps, action, environnement. Cognition incarnée et ergonomie cognitive.

---

## Formulation synthétique

La connaissance scientifique permet d’identifier les systèmes de signes par lesquels un humain manifeste son activité et son interaction avec son environnement. Ces signes peuvent être comportementaux, langagiers, physiologiques ou neurophysiologiques. En les enregistrant dans le temps et en les reliant au contexte, on construit des **modèles probabilistes d’états latents** (charge cognitive, engagement, fatigue, activation). Ces modèles ne lisent pas l’intériorité : ils produisent des hypothèses avec un degré d’incertitude. La représentation de ces états permet de concevoir des interfaces **adaptatives, explicables et centrées sur l’humain**.

---

## Principes de conception retenus

- Distinguer **mesure**, **interprétation** et **action**.
- Afficher l’**incertitude** plutôt qu’une certitude artificielle.
- Utiliser une **ligne de base** propre à chaque personne.
- Conserver l’historique temporel et le contexte (le temps de la session, pas au-delà sans nécessité).
- Permettre à l’utilisateur de **corriger** l’interprétation.
- **Minimiser** les données collectées.
- Documenter la **durée de conservation**.
- Ne pas utiliser une estimation comme **diagnostic médical**.
- Ne pas déclencher automatiquement une **décision à fort impact**.
- Rendre visibles les résultats du modèle et leur interprétation (interfaces BCI explicables).

Recommandations CNIL à documenter : collecte, sécurité, profils, conservation, droits des personnes.

---

## Trois questions de cadrage (réponses détaillées à part)

1. Quel format de code HTML pour le dashboard ? → `docs/format-html.md`
2. Quels indicateurs visuels pour l’incertitude ? → `docs/incertitude.md`
3. Comment appliquer la minimisation des données ? → `docs/minimisation.md`

---

## Pistes pour la suite (visualisation livrable)

- Vocabulaire contrôlé des signaux et des états.
- Modèle de données temporel (déjà ébauché dans `data/session-simulee.json`).
- Tester le dashboard avec des données simulées (ce prototype).
- Capteurs réels uniquement avec consentement explicite, plus tard.
- Documenter limites scientifiques, éthiques et techniques.
- Réutiliser ce prototype comme base de visualisation livrable dans un autre projet.
