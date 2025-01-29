---
apiPath: "/api/geo/intercommunalites/:code"
files: []
order: 7
visible: true
---
Renvoit une intercommunalite via son code SIREN

### Format de la réponse
La réponse est un JSON contenant les informations suivantes :

https://docurba.beta.gouv.fr/api/geo/intercommunalites/200000172
```json
{
  "code": "200000172",
  "type": "Intercommunalite",
  "dateCreation": "2019-01-01",
  "intituleSansArticle": "Faucigny-Glières",
  "intituleComplet": "Communauté de communes Faucigny-Glières",
  "categorieJuridique": "Communauté de communes",
  "intitule": "Faucigny-Glières",
  "communes": [
    {
      "code": "74024",
      "type": "Commune",
      "dateCreation": "1943-01-01",
      "intituleSansArticle": "Ayse",
      "intitule": "Ayse"
    },
    {
      "code": "74042",
      "type": "Commune",
      "dateCreation": "1964-12-17",
      "intituleSansArticle": "Bonneville",
      "intitule": "Bonneville"
    },
    {
      "code": "74049",
      "type": "Commune",
      "dateCreation": "1943-01-01",
      "intituleSansArticle": "Brizon",
      "intitule": "Brizon"
    },
    {
      "code": "74087",
      "type": "Commune",
      "dateCreation": "1943-01-01",
      "intituleSansArticle": "Contamine-sur-Arve",
      "intitule": "Contamine-sur-Arve"
    },
    {
      "code": "74164",
      "type": "Commune",
      "dateCreation": "1943-01-01",
      "intituleSansArticle": "Marignier",
      "intitule": "Marignier"
    },
    {
      "code": "74212",
      "type": "Commune",
      "dateCreation": "2019-01-01",
      "intituleSansArticle": "Glières-Val-de-Borne",
      "intitule": "Glières-Val-de-Borne"
    },
    {
      "code": "74312",
      "type": "Commune",
      "dateCreation": "1943-01-01",
      "intituleSansArticle": "Vougy",
      "intitule": "Vougy"
    }
  ],
  "competences": {
    "scot": true,
    "secteur": true,
    "plu": false
  },
  "departementCode": "74",
  "nbCommunes": 7,
  "labelJuridique": "CC"
}
```
