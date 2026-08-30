# ui/data

`profile.json` est la **sortie du moteur** (contrat `DecodedHuman`) que
l'interface lit. Le fichier est régénéré à chaque décodage :

```bash
# depuis la racine du dépôt
python -m language_decoder.cli decode --input profil.txt --title "Nom" --person h-001
#   (écrit ui/data/profile.json)

# ou via l'interface (bouton « Décoder ») une fois le serveur lancé :
python -m language_decoder serve --port 9000
```

Ce fichier est versionné comme **exemple de démonstration**. Il ne doit pas
contenir de données personnelles réelles sans consentement.
