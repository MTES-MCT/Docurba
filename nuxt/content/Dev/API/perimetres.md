---
apiPath: "/api/perimetres"
files: []
order: 3
visible: true
---

https://docurba.beta.gouv.fr/api/perimetres?departement=01

https://docurba.beta.gouv.fr/api/perimetres?departement=01&avant=2025-01-01

### Description

Retourne les procédures de chaque commune et leur opposabilité.

### Requête

#### Endpoint

`/api/perimetres`

#### Paramètres de requête disponibles

- `departement` : Filtrer par le code INSEE du département.
- `avant` : Ne prend en compte que les événements avant ce jour, au format `YYYY-MM-DD`.

### Réponse

La réponse est un CSV avec les colonnes suivantes :

- `annee_cog` : Pour l'instant codé en dur avec la valeur `2024`
- `collectivite_code` : Code INSEE de la commune associée
- `collectivite_type` : Type de la commune associée
- `procedure_id` : Identifiant de la procédure liée
- `type_document` : Type de document d'urbanisme parmi `CC`, `POS`, `PLU`, `PLUi`, `PLUiH`, `PLUiHM`, `PLUiM`, `SCOT`, `SD`
- `opposable` : `True` si la procédure est opposable, `False` sinon
