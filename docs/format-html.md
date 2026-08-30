# Format HTML recommandé pour le dashboard

Réponse à : *« Quel format de code HTML recommandes-tu pour le dashboard ? »*

## Recommandation

**HTML5 sémantique, francophone (`lang="fr"`), sans framework et sans dépendance distante.** La structure vit dans `index.html`, la présentation dans `css/dashboard.css`, le comportement dans `js/dashboard.js`, les données dans `data/session-simulee.json`.

Ce format est volontairement plat : le prototype doit pouvoir être repris plus tard comme visualisation livrable, inspecté dans le navigateur, ouvert sans chaîne de build.

## Pourquoi ce format

| Option | Verdict |
| --- | --- |
| Page unique inline (HTML+CSS+JS) | Portable, mais illisible dès que le modèle grossit. |
| React / Vue / Svelte | Trop lourd pour un livrable de recherche ; masque la sémantique. |
| Canvas / WebGL d’emblée | Inaccessible, non indexable, mauvais pour l’incertitude textuelle. |
| **HTML5 + CSS + JS + JSON** | Inspectable, accessible, réutilisable, aligné avec la minimisation (aucun script tiers). |

Aucun CDN, aucune police distante, aucun tracker. Charger une fonte ou un analytics serait contradictoire avec la minimisation et la confidentialité.

## Règles de structure

1. **Landmarks** : `header`, `main`, `section`, `aside`, `footer`. Une ancre « aller au contenu ».
2. **Une section = une couche du raisonnement** : cas, langages, mesures, hypothèses, temps, action, minimisation, représentation. Ne pas tout fusionner dans une grille décorative.
3. **Titres hiérarchiques** : un seul `h1`, puis `h2` par carte. Les lecteurs d’écran doivent pouvoir sauter de couche en couche.
4. **Mesure ≠ inférence dans le DOM** : les valeurs observées sont du texte / des `data-*` ; les états estimés portent `data-kind="inference"` et ne sont jamais des `<meter>` (un `meter` suggère une grandeur connue, pas une hypothèse).
5. **Données hors du HTML** : le JSON est la source. Le HTML initial sert de secours (progressive enhancement) si le script échoue.
6. **Contrôles natifs** : `button`, `input type="checkbox"` pour le consentement par modalité. Pas de `div` cliquable.
7. **Nombres tabulaires** : `font-variant-numeric: tabular-nums` pour comparer T1…Tn.
8. **Nom accessible** pour chaque graphique (`aria-label` / `role="img"` sur le SVG).
9. **Mouvement** : respecter `prefers-reduced-motion`.
10. **Impression** : le dashboard reste lisible en noir et blanc (hachures + libellés, pas la couleur seule).

## Ce qu’il ne faut pas faire

- Feux tricolores rouge / orange / vert pour un état intérieur (effet diagnostic).
- Camembert d’émotions qui somment à 100 %.
- `<meter>` ou barre pleine unique pour « l’émotion détectée ».
- Images de cerveau ou de cœur « temps réel » qui simulent une lecture.
- Attributs `title` seuls pour l’incertitude (invisibles au clavier et au tactile).

## Gabarit type d’une hypothèse

```html
<article class="hypothese" data-kind="inference" data-id="charge_cognitive">
  <h3>Charge cognitive élevée</h3>
  <p>
    Estimation <span class="num">68 %</span>
    <span class="ci">intervalle 52 – 79 %</span>
  </p>
  <div class="estime"
       style="--p:.68;--lo:.52;--hi:.79"
       role="img"
       aria-label="Point 68 pour cent, intervalle de 52 à 79">
    <span class="estime-piste"></span>
  </div>
  <p class="preuves">Preuves : FC, HRV, temps, erreurs — pas une lecture directe.</p>
</article>
```

Le point d’estimation et l’intervalle sont dans le texte **et** dans le graphique. La redondance est volontaire : l’incertitude ne doit pas dépendre de la vue.

## Réemploi dans un autre projet

Pour une visualisation livrable ultérieure, conserver :

- les `data-kind` (`measure` | `inference` | `action` | `context`) ;
- le JSON de session comme contrat ;
- les classes d’incertitude (`.estime`, `.hachure`, `.mesure`) ;
- l’absence de build.

On pourra alors changer le habillage sans casser le modèle.
