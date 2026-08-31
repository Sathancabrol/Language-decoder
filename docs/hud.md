# Structure abstraite du HUD HCSM

Cinq zones. Charge cognitive minimale, réactivité maximale. Les images : `hud-hcsm-kei.jpg` (flux K·E·I + métriques live), `hud-accueil-utilisateur.jpg` (home centrée utilisateur), `hud-flux-inferences.jpg` (Sankey d’inférence).

## 1. Centre — nœud focal

Objet d’étude à T0. Ici : le **flux épistémique**, pas un avatar.

```
K  Knowledge     construits · ce que la science sait
        ↓
E  Evidence      features observées · pas le brut
        ↓
I  Inference     conclusion ou Refusal
```

Méthodes d’affichage des flux : alluvial / Sankey, Bézier, brushing. Soutien = trait plein cyan/teal. Réfutation = tirets ocre/rose. Un nœud I porte **point + intervalle**, jamais un % nu.

Hotspots : Isoler · Analyser · Refuser d’estimer.

## 2. Gauche — état et métriques live

Constantes de **session**, pas un profil de personnalité.

- FC vs ligne de base
- HRV relative
- temps sur tâche, erreurs
- couverture des langages (4/8)
- radar = modalités collectées
- sparklines temporelles
- badge Nominal / données insuffisantes — pas Critical médical

## 3. Droite — inférence et contrôle

Inspecteur `ConstructEstimate` : valeur, intervalle, preuves, alternatives, warrant / rebuttal.  
Actions utilisateur : proposer une aide (réversible), ignorer, corriger. L’humain tranche.

## 4. Cadre — header et dock

- Header : id anonyme, **LIVE**, T0 UTC, version
- Dock : Accueil · Cognition / graphe · Signaux · Temps · Système  
  Pas Métiers, pas inventaire, pas debuffs.

## 5. Affordance

Verre sombre translucide. Cyan = donnée / structure. Teal = évidence. Ocre = inférence. Rose = refus ou réfutation seulement.

## Hardware (archive, hors prototype logiciel)

Le fil mobiGlas / Pepper’s Ghost / plasma est documenté dans `docs/hud-hardware.md`. L’outil actuel reste un HUD **écran**. Le banc optique vient après le logiciel.
