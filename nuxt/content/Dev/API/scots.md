---
apiPath: "/api/scots"
files: []
order: 2
visible: true
---

https://docurba.beta.gouv.fr/api/scots?departement=01

https://docurba.beta.gouv.fr/api/scots?departement=01&avant=2025-01-01

### Description

Cet endpoint retourne les collectivités porteuses de procédures SCoTs par combinaison SCoT opposable/SCoT en cours.

⚠️ **Note importante :**
Lorsqu'une collectivité porte plusieurs SCoT opposables, il y a une ligne par SCoT opposable et chacune de ces lignes répète la procédure en cours.

Ici la préposition `scot_` fait en faire référence à la collectivité porteuse des procédures de type SCOT de l'export.

### Requête

#### Endpoint

`/api/scots`

#### Paramètres de requête disponibles

- `departement` : Filtrer par le code INSEE du département.
- `avant` : Ne prend en compte que les événements jusqu'à ce jour, au format `YYYY-MM-DD`.

### Réponse

La réponse est un CSV avec les colonnes suivantes :

Pour la collectivité :

- `annee_cog` : Pour l'instant codé en dur avec la valeur `2024`
- `scot_code_region` : Code INSEE de la région
- `scot_libelle_region` : Nom de la région
- `scot_code_departement` : Code INSEE du département
- `scot_lib_departement` : Nom du département
- `scot_codecollectivite` : SIREN de la collectivité porteuse
- `scot_code_type_collectivite` : Type de collectivité
- `scot_nom_collectivite` : Nom de la collectivité porteuse

<br>
Pour le SCoT opposable :

- `pa_nom_schema` : Nom du document
- `pa_id` : Identifiant Docurba
- `pa_noserie_procedure` : Identifiant Sudocuh, optionnel
- `pa_scot_interdepartement` : Indique si le SCoT est interdépartemental
- `pa_date_publication_perimetre` : Date de publication du périmètre
- `pa_date_prescription` : Date de prescription
- `pa_date_arret_projet` : Date d'arrêt de projet
- `pa_date_approbation` : Date d'approbation
- `pa_annee_approbation` : Année d'approbation
- `pa_date_fin_echeance` : Date de fin d'échéance
- `pa_nombre_communes` : Nombre de communes dans le périmètre de la procédure

<br>
Pour le SCoT en cours :

- `pc_nom_schema` : Nom du document
- `pc_id` : Identifiant Docurba
- `pc_noserie_procedure` : Identifiant Sudocuh, optionnel
- `pc_proc_elaboration_revision` : Type de procédure en cours (élaboration, révision, etc.)
- `pc_scot_interdepartement` : Indique si le SCoT est interdépartemental
- `pc_date_publication_perimetre` : Date de publication du périmètre
- `pc_date_prescription` : Date de prescription
- `pc_date_arret_projet` : Date d'arrêt de projet
- `pc_nombre_communes` : Nombre de communes dans le périmètre de la procédure

<br>
Toutes les dates sont au format ISO 8601.
