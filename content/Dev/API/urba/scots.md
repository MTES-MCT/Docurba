---
apiPath: "/api/urba/exports/scots"
files: []
order: 10
visible: true
---
## Documentation de l'API : `/api/urba/exports/scots`

### Description
Cet endpoint retourne les données des procédures SCOTS par combinaison SCOT en cours/SCOT opposable. 

⚠️ **Note importante :**  
Une collectivité porteuse peut avoir plusieurs procédures opposables, et donc la même procédure en cours peut apparaître plusieurs fois.

Ici la préposition `scot_` fait en faire référence à la collectivité porteuse des procédures de type SCOT de l'export.

---

### Format de la requête

#### Endpoint
`/api/urba/exports/scots`

#### Paramètres de requête
Aucun paramètre de requête disponible, car les fichiers générés sont plus petits.

---

### Format de la réponse

La réponse est un objet JSON contenant les informations suivantes :

```json
{
  "annee_cog": "Année de référence pour le COG (Code Officiel Géographique)", // Number
  "scot_code_region": "Code de la région", // String
  "scot_libelle_region": "Nom de la région", // String
  "scot_code_departement": "Code du département", // String
  "scot_lib_departement": "Nom du département", // String
  "scot_codecollectivite": "SIREN de la collectivité porteuse", // String
  "scot_code_type_collectivite": "Type de collectivité", // String
  "scot_nom_collectivite": "Nom de la collectivité porteuse", // String
  "pa_nom_schema": "Nom du document opposable", // String
  "pa_id": "Identifiant du document opposable", // String
  "pa_noserie_procedure": "Numéro de série de la procédure opposable (Sudocuh)", // String
  "pa_scot_interdepartement": "Indique si le SCOT est interdépartemental", // Boolean
  "pa_date_publication_perimetre": "Date de publication du périmètre de la procédure opposable (ISO)", // String
  "pa_date_prescription": "Date de prescription de la procédure opposable (ISO)", // String
  "pa_date_arret_projet": "Date d'arrêt de projet de la procédure opposable (ISO)", // String
  "pa_date_approbation": "Date d'approbation de la procédure opposable (ISO)", // String
  "pa_annee_approbation": "Année d'approbation de la procédure opposable", // Number
  "pa_date_approbation_precedent": "Date d'approbation de la procédure opposable précédente (ISO)", // String
  "pa_date_fin_echeance": "Date de fin d'échéance de la procédure opposable (ISO)", // String
  "pa_nombre_communes": "Nombre de communes dans le périmètre de la procédure opposable", // Number
  "pc_nom_schema": "Nom du document en cours", // String
  "pc_id": "Identifiant du document en cours", // String
  "pc_noserie_procedure": "Numéro de série de la procédure en cours (Sudocuh)", // String
  "pc_proc_elaboration_revision": "Type de procédure en cours (élaboration, révision, etc.)", // String
  "pc_scot_interdepartement": "Indique si le SCOT en cours est interdépartemental", // Boolean
  "pc_date_publication_perimetre": "Date de publication du périmètre de la procédure en cours (ISO)", // String
  "pc_date_prescription": "Date de prescription de la procédure en cours (ISO)", // String
  "pc_date_arret_projet": "Date d'arrêt de projet de la procédure en cours (ISO)", // String
  "pc_nombre_communes": "Nombre de communes dans le périmètre de la procédure en cours", // Number
}