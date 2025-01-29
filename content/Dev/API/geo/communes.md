---
apiPath: "/api/geo/communes"
files: []
order: 10
visible: true
---
Listes des communes de France au format INSEE et enrichie du code Intercomunalité. Il est possible de filtrer sur chaque clé.

https://docurba.beta.gouv.fr/api/geo/communes?code=01001

### Format de la réponse

La réponse est un JSON contenant les informations suivantes :

```json
[{
  "code": "01001",
  "type": "Commune",
  "dateCreation": "1943-01-01",
  "intituleSansArticle": "Abergement-Clémenciat",
  "intitule": "L'Abergement-Clémenciat",
  "intercommunaliteCode": "200069193",
  "departementCode": "01"
}]
```
