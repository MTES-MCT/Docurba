---
apiPath: "/api/communes"
files: []
order: 1
visible: true
---

https://docurba.beta.gouv.fr/api/communes?departement=01

https://docurba.beta.gouv.fr/api/communes?departement=01&avant=2025-01-01

### Description

Cet endpoint retourne les données par communes avec des informations sur l'intercommunalité, la collectivité porteuse, le plan en cours et le plan opposable.

### Requête

#### Endpoint

`/api/communes`

#### Paramètres de requête disponibles

- `departement` : Filtrer par le code INSEE du département.
- `avant` : Ne prend en compte que les événements avant ce jour, au format `YYYY-MM-DD`.

### Réponse

La réponse est un CSV avec les colonnes suivantes :

Pour la commune :

- `annee_cog` : Pour l'instant codé en dur avec la valeur `2024`
- `code_insee` : Code INSEE de la commune
- `com_nom` : Nom de la commune
- `com_code_departement` : Code INSEE du département
- `com_nom_departement` : Nom du département
- `com_code_region` : Code INSEE de la région
- `com_nom_region` : Nom de la région
- `com_nouvelle` : Booléen indiquant si c'est c'est une commune nouvelle
- `plan_code_etat_simplifie` : Code État sur 2 chiffres
- `plan_libelle_code_etat_simplifie` : Libellé du code État simplifié
- `plan_code_etat_complet` : Code état sur 4 chiffres
- `plan_libelle_code_etat_complet` : Libellé du code État complet

<br>
Pour l'intercommunalité, si elle existe :

- `epci_reg` : Code INSEE de la région
- `epci_region` : Nom de la région
- `epci_dept` : Code INSEE du département
- `epci_departement` : Nom du département
- `epci_type` : Type d'intercommunalité
- `epci_nom` : Nom de l'intercommunalité
- `epci_siren` : SIREN de l'intercommunalité

<br>
Pour la collectivité porteuse :

- `collectivite_porteuse` : Code INSEE
- `cp_type` : Type de la collectivité
- `cp_code_region` : Code INSEE de la région
- `cp_lib_region` : Nom de la région
- `cp_code_departement` : Code INSEE du département
- `cp_nom_departement` : Nom du département
- `cp_nom` : Nom de la collectivité
- `cp_siren` : SIREN si la collectivité porteuse est une intercommunalité
- `cp_code_insee` : Code INSEE si la collectivité porteuse est une commune

<br>
Pour le plan en cours :

- `pc_docurba_id` : Identifiant Docurba
- `pc_num_procedure_sudocuh` : Identifiant Sudocuh, optionnel
- `pc_nb_communes` : Taille du périmètre de plan
- `pc_type_document` : Type de document
- `pc_type_procedure` : Type de procédure
- `pc_date_prescription` : Date de prescription
- `pc_date_arret_projet` : Date d'arrêt de projet
- `pc_date_pac` : Date de porter à connaissance
- `pc_date_pac_comp` : Date de porter à connaissance complémentaire
- `pc_plui_valant_scot` : Booléen indiquant si ce plan vaut SCoT
- `pc_pluih` : Booléen indiquant si ce plan vaut PLH
- `pc_pdu_tient_lieu` : Booléen indiquant si ce plan vaut PDM
- `pc_sectoriel` : Booléen indiquant si le plan est sectoriel
- `pc_pdu_obligatoire` : Booléen indiquant si un PDU est obligatoire
- `pc_nom_sst` : Nom du prestataire externe
- `pc_cout_sst_ht` : Coût HT
- `pc_cout_sst_ttc` : Coût TTC

<br>
Pour le plan opposable :

- `pa_docurba_id` : Identifiant Docurba
- `pa_num_procedure_sudocuh` : Identifiant Sudocuh, optionnel
- `pa_nb_communes` : Taille du périmètre de ce plan
- `pa_type_document` : Type de document
- `pa_type_procedure` : Type de procédure
- `pa_date_prescription` : Date de prescription
- `pa_date_arret_projet` : Date d'arrêt de projet
- `pa_date_pac` : Date de porter à connaissance
- `pa_date_pac_comp` : Date de porter à connaissance complémentaire
- `pa_date_approbation` : Date d'approbation
- `pa_annee_prescription` : Année de prescription
- `pa_annee_approbation` : Année d'approbation
- `pa_date_executoire` : Date du caractère exécutoire
- `pa_delai_approbation` : Nombre de jours entre la prescription et l'approbation
- `pa_plui_valant_scot` : Booléen indiquant si ce plan vaut SCoT
- `pa_pluih` : Booléen indiquant si ce plan vaut PLH
- `pa_pdu_tient_lieu` : Booléen indiquant si ce plan vaut PDM
- `pa_sectoriel` : Booléen indiquant si le plan est sectoriel
- `pa_pdu_obligatoire` : Booléen indiquant si un PDU est obligatoire
- `pa_nom_sst` : Nom du prestataire externe
- `pa_cout_sst_ht` : Coût HT
- `pa_cout_sst_ttc` : Coût TTC

<br>
Toutes les dates sont au format ISO 8601.
