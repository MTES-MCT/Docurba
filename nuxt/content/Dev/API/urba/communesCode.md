---
apiPath: "/api/urba/exports/communes"
files: []
order: 10
visible: true
---
https://nuxt3.docurba.incubateur.net/api/urba/exports/communes?departementCode=56

### Description
Cet endpoint retourne les données procédures par communes.

---

### Format de la requête

#### Endpoint
GET `/api/urba/exports/communes`

#### Paramètres de requête disponibles :
1. **`csv=true`**  
   - Permet d'obtenir le résultat au format CSV au lieu de JSON.

2. **Filtres sur les attributs des communes**  
   Vous pouvez filtrer les communes en ajoutant des paramètres de requête basés sur les attributs suivants :
   - `code` : Le code INSEE de la commune.
   - `siren` : Le code SIREN de la commune.
   - `regionCode` : Le code de la région.
   - `departementCode` : Le code du département.
   - `intercomunaliteCode` : Le code de l'intercommunalité.
   - `competencePLU` : La compétence de la commune en matière de PLU (Plan Local d'Urbanisme) true/false.

---

### Format de la réponse

La réponse est une liste d'objets, chaque objet représentant les données d'une commune. Voici la structure de la réponse :

```json
{
  "epci_reg": "Code de la région de l'intercommunalité", // String
  "epci_region": "Nom de la région de l'intercommunalité", // String
  "epci_dept": "Code du département de l'intercommunalité", // String
  "epci_departement": "Nom du département de l'intercommunalité", // String
  "epci_type": "Type d'intercommunalité", // String
  "epci_nom": "Nom de l'intercommunalité", // String
  "epci_siren": "SIREN de l'intercommunalité", // String
  "com_nom": "Nom de la commune", // String
  "collectivite_porteuse": "Code INSEE ou SIREN de la commune ou de l'intercommunalité porteuse", // String
  "plan_etat_code1": "Code état 1 sudocuh", // String
  "plan_libelle_etat_code1": "Libellé du code état 1 sudocuh", // String
  "plan_etat_code2": "Code état 2 sudocuh", // String
  "plan_libelle_etat_code2": "Libellé du code état 2 sudocuh", // String
  "plan_code_etat_bcsi": "Code état BCSI", // String
  "plan_libelle_code_etat_bcsi": "Libellé du code état BCSI", // String
  "types_pc": "Types de procédures principales en cours", // String
  "pc_num_procedure": "Identifiant sudocuh de la procédure principale en cours", // Number
  "pc_nb_communes": "Nombre de communes dans le périmètre de la procédure en cours", // Number
  "pc_type_document": "Type de document du plan en cours", // String
  "pc_type_procedure": "Type de procédure en cours", // String
  "pc_date_prescription": "Date ISO de la prescription en cours", // String
  "pc_date_arret_projet": "Date ISO de l'arrêt de projet en cours", // String
  "pc_date_pac": "Date ISO du PAC en cours", // String
  "pc_date_pac_comp": "Date ISO de la complétion du PAC en cours", // String
  "pc_plui_valant_scot": "Le plan en cours vaut SCOT", // Boolean
  "pc_pluih": "Le plan en cours est un PLUIH", // Boolean
  "pc_sectoriel": "Le plan en cours est sectoriel", // Boolean
  "pc_pdu_tient_lieu": "Le plan en cours tient lieu de PDU", // Boolean
  "pc_pdu_obligatoire": "Le plan en cours rend le PDU obligatoire", // Boolean
  "pa_id": "Identifiant Docurba du document opposable", // String
  "pa_num_procedure": "Identifiant sudocuh de la procédure opposable", // Number
  "pa_nb_communes": "Nombre de communes dans le périmètre du plan opposable", // Number
  "pa_type_document": "Type de document du plan opposable", // String
  "pa_type_procedure": "Type de procédure opposable", // String
  "pa_sectoriel": "Le plan opposable est sectoriel", // Boolean
  "pa_date_prescription": "Date ISO de la prescription opposable", // String
  "pa_date_arret_projet": "Date ISO de l'arrêt de projet opposable", // String
  "pa_date_pac": "Date ISO du PAC opposable", // String
  "pa_date_pac_comp": "Date ISO de la complétion du PAC opposable", // String
  "pa_date_approval": "Date ISO de l'approbation du plan opposable", // String
  "pa_plui_valant_scot": "Le plan opposable vaut SCOT", // Boolean
  "pa_pluih": "Le plan opposable est un PLUIH", // Boolean
  "pa_pdu_tient_lieu": "Le plan opposable tient lieu de PDU", // Boolean
  "pa_pdu_obligatoire": "Le plan opposable rend le PDU obligatoire", // Boolean
  "proc_nb_revisions": "Nombre de révisions", // Number
  "proc_nb_modifications": "Nombre de modifications", // Number
}

