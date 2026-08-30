# Fondements littéraires — Language-decoder

Ce moteur n'invente pas ses concepts : il les emprunte à des travaux établis et
réutilise les ontologies déjà construites dans l'écosystème (HCSM, Cognitorium,
état-de-l'art psychologie).

## 1. Ontologie & alignements

- **Cognitive Atlas** — Poldrack et al. (2011) : fondation de connaissance de la
  neurosciences cognitive ; identifiants externes primaires.
- **RDoC** — Insel, Cuthbert et al. (2010) : unités d'analyse (voies), pas d'un
  classifieur clinique.
- **ICF** — WHO (2001) : fonctions corporelles (b*), activités (d*), participation.
- **HPO** — Köhler et al. (2024).

Règle : identifiants externes primaires, identifiants HCSM = ponts. `owl:sameAs`
interdit entre Construct et ExternalConcept en v0.1.

## 2. Validité & rigueur

- **Cronbach & Meehl (1955)** : validité de construit. Un instrument ≠ un
  construit (n-back ≠ mémoire de travail ; RT variability ≠ attention).
- **Borsboom & Cramer (2013), Kane (2013)** : réseaux & validation d'interprétation.
- Le moteur n'additionne pas des voies différentes (EEG + Likert) : il les
  **confronte** ; la convergence réduit σ, la divergence l'augmente.

## 3. Cognition (domaine mental)

Processus issus de la taxonomie Cognitorium / état-de-l'art :

- Perception, attention (sélective, soutenue, divisée, exécutive).
- Mémoire de travail (Baddeley), mémoire à long terme (épisodique, sémantique,
  procédurale, Squire / Tulving).
- Langage & pragmatique.
- Raisonnement & résolution de problèmes.
- Contrôle exécutif (Miyake : inhibition, flexibilité, mise à jour).
- Métacognition & auto-régulation (Flavell 1979 ; Zimmerman 2000).
- Émotion, motivation, cognition sociale (théorie de l'esprit).

## 4. Fonctionnement / dynamique (domaine dynamics)

- **Courbe d'oubli** — Ebbinghaus (1885) : décroissance exponentielle vers un
  plancher résiduel (mémoire cristallisée).
- **Loi de puissance de la pratique** — Newell & Rosenbloom (1981) : la
  réactivation est plus rapide que le primo-apprentissage.
- **Transfert** — Thorndike & Woodworth (1901) : transposabilité des compétences.
- **État vs trait** — Steyer et al. ; HCSM `CapacityProfile` (disposition lente,
  pas un état T0).
- **Charge cognitive / allocation d'effort** — Wickens, Kahneman.
- **Évaluation écologique momentanée (EMA)** — Shiffman et al. (2008) ; phénotypage
  numérique (Onnela 2016).

## 5. Capacité d'action (domaine action)

- **CAPABILITY** (Sen) et **ICF activités (d*)** : ce que la personne **peut**
  faire, distinct de ce qu'elle fait (performance).
- Séparation stricte capacité/performance — une projection est une hypothèse.

## 6. Provenance & reproductibilité

- **FAIR** — Wilkinson et al. (2016) ; **PROV-O** — W3C (2013).

## Frontières (ce que le moteur ne fait pas)

- Ne produit pas de **conclusion psychologique** (L5) automatiquement.
- Ne produit pas de **score global de fonctionnement cognitif**.
- Ne traduit pas un état bas en **restriction de participation**, ni en
  justification scolaire / médicale / managériale.
- Ne fait pas de **diagnostic** ; les canaux `genes/molecules/cells` RDoC sont
  hors périmètre v0.1.
