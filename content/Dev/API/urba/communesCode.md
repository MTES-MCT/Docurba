---
apiPath: "/api/urba/communes/:code"
files: []
order: 10
visible: true
---
Renvoit les données d'urbanisme d'une commune.

https://docurba.beta.gouv.fr/api/urba/communes/01001
```json
{
  "region_name": "Auvergne-Rhône-Alpes",      // eq: EPCI_REGION2016
  "interco_departement_code": "01",           // eq: EPCI_DEPT
  "commune_departement_code": "01",           // eq: INSEE_DEPT
  "commune_name": "L'Abergement-Clémenciat",  // eq: INSEE_COMMUNE
  "interco_siren": "200069193",               // eq: EPCI_SIREN
  "interco_name": "La Dombes",                // eq: EPCI_NOM
  "interco_competence_scot": true,            // ADDED
  "interco_competence_secteur": true,         // ADDED
  "interco_competence_plu": false,            // ADDED
  "commune_du_opposable": "PLU",              // eq: DU_OPPOSABLE
  "commune_du_in_progress": "",               // ADDED
  "state_code": "39",                         // eq: DU_CODE_ETATS
  "state_label": "PLU approuvé"               // eq: DU_LIBELLE_ETATS
}
```
