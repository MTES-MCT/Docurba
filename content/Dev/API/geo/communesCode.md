---
apiPath: "/api/geo/communes/:code"
files: []
order: 9
visible: true
---
Récupère une commune via son code INSEE.

https://docurba.beta.gouv.fr/api/geo/communes/01001

### Format de la réponse
La réponse est un JSON contenant les informations suivantes :


```json
{
  "code": "01001",
  "type": "Commune",
  "dateCreation": "1943-01-01",
  "intituleSansArticle": "Abergement-Clémenciat",
  "intitule": "L'Abergement-Clémenciat",
  "intercommunaliteCode": "200069193",
  "departementCode": "01"
}
```
