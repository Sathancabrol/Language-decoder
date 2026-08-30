# Indicateurs visuels de l’incertitude

Réponse à : *« Quels indicateurs visuels utiliser pour montrer l’incertitude ? »*

L’incertitude est un **contenu**, pas un disclaimer. Un biomarqueur isolé n’est pas une preuve émotionnelle ; le dashboard doit le rendre visible sans effort.

## Principes

1. **Jamais un seul nombre nu.** Toute inférence porte un point **et** un intervalle.
2. **Plusieurs hypothèses à la fois.** Elles ne sont pas exclusives et ne somment pas à 100 %.
3. **Mesuré ≠ inféré.** Trait plein / carte stable pour la mesure ; hachure, tirets, encre ocre pour l’inférence.
4. **L’absence d’information se voit.** Qualité de signal, modalités non collectées, « données insuffisantes ».
5. **Pas de sémantique d’alarme.** Pas de rouge = danger émotionnel. L’ocre signale l’hypothèse, le teal la mesure.
6. **Texte d’abord.** Un lecteur d’écran, une impression ou un export JSON doivent porter la même incertitude.

## Indicateurs retenus dans le prototype

| Indicateur | Rôle | Forme |
| --- | --- | --- |
| Point + intervalle | Confiance d’une hypothèse | Piste 0–1, bande hachurée `[lo, hi]`, point pour `p` |
| Hypothèses concurrentes | Ambiguïté réelle | Liste triée, non exclusive, alternatives nommées |
| Hachure | « Ceci est estimé » | `repeating-linear-gradient` + bordure tiretée |
| Trait plein | « Ceci est mesuré » | Bordure continue, encre teal |
| Écart à la ligne de base | Éviter l’absolu (92 bpm sans 68) | `92 bpm · +24 vs repos 68` |
| Qualité de signal | Fiabilité de l’acquisition | Points `●●●●○` + pourcentage |
| Bande temporelle | Incertitude qui évolue | Aire entre `lo` et `hi` sur T1…Tn |
| Preuves citées | Explicabilité | Liste des features utilisées, pas du « modèle magique » |
| Correction | L’humain tranche | Correspond / Ne correspond pas / Je ne sais pas |
| Badge simulation | Statut épistémique global | « Données simulées » toujours visible |

## Détail : piste d’estimation

```
0                         p                      1
|-----------[=====●=====]------------------------|
            lo         hi
```

- La piste claire = toute l’échelle, pour rappeler que 68 % n’est pas « presque sûr » dans l’absolu.
- La bande hachurée = intervalle de crédibilité simulé.
- Le point = estimation ponctuelle.
- Les trois valeurs sont aussi écrites en chiffres.

Si l’intervalle s’élargit (moins de langages collectés), la bande s’étale. C’est le geste visuel de la minimisation : **moins de données, plus d’incertitude**, pas un silence du système.

## Détail : courbe temporelle

Une ligne d’estimation ne suffit pas. On dessine :

- une **aire** `lo–hi` (incertitude) ;
- une **ligne** de l’estimation ;
- des **points** T1, T2, T3, T4, maintenant ;
- un libellé « tendance possible, pas une prédiction certaine ».

Si l’aire s’évase vers la droite, le futur est plus incertain que le passé — comportement honnête pour une prévision.

## Détail : alternatives à un même signal

Sous le cardio, une ligne :

> Une FC élevée peut indiquer : effort, excitation, stress, peur, douleur, déplacement.

Ce n’est pas décoratif : c’est l’antidote à la lecture unique. Le prototype affiche ces alternatives à côté de l’hypothèse dominante.

## Ce qui a été écarté

| Motif | Pourquoi |
| --- | --- |
| Jauge unique « émotion 82 % » | Fausse précision, une dimension pour un phénomène multimodal. |
| Heatmap cérébrale | Implication de lecture neurale, hors données et hors éthique du prototype. |
| Smileys | Réduisent l’état à une valence, contredisent la charge cognitive. |
| Clignotement / rouge | Connotation médicale ou d’alerte de sécurité. |
| Barres empilées à 100 % | Les hypothèses se recouvrent ; une normalisation forcée ment. |

## Copie d’écran mentale pour le livrable ultérieur

Conserver au minimum, dans toute visualisation future :

1. intervalle autour du point ;
2. au moins deux hypothèses ;
3. la ligne de base ;
4. la mention que l’état est **estimé** ;
5. le bouton de correction.
