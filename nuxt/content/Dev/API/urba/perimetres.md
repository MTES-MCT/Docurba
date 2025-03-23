---
apiPath: "/api/perimetres"
files: []
order: 10
visible: true
---

https://docurba.beta.gouv.fr/exports/perimetres?departement=01

### Description

Retourne les procédures de chaque commune et leur opposabilité.

### Requête

#### Endpoint

`/api/perimetres`

#### Paramètres de requête disponibles

- `departement` : Filtrer par le code INSEE du département.

### Réponse

La réponse est un CSV avec les colonnes suivantes :

- `collectivite_code` : Code INSEE de la commune associée
- `collectivite_type` : Type de la commune associée
- `procedure_id` : Identifiant de la procédure liée
- `opposable` : `True` si la procédure est opposable, `False` sinon
