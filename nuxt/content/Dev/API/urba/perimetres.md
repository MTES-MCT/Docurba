---
apiPath: "/api/urba/exports/perimetres"
files: []
order: 10
visible: true
---
https://nuxt3.docurba.incubateur.net/api/urba/exports/perimetres?departement=01

### Description
Cet endpoint retourne code INSEE des communes par procédures.

---

### Format de la requête

#### Endpoint
`/api/urba/exports/perimetres`

#### Paramètres de requête disponibles :
1. **Filtres sur les attributs**  
   Vous pouvez filtrer les résultats en utilisant les paramètres suivants :
   - `collectivite_code` : Filtrer par le code de la collectivité. Utile pour retrouver l'historique des procédures d'une commune.
   - `collectivite_type` : Filtrer par le type de collectivité. `collectivite_type=COM` permet d'exclure les COMD.
   - `procedure_id` : Filtrer par l'identifiant de la procédure.
   - `opposable` : Filtrer selon si le périmètre est opposable (`true` ou `false`).
   - `departement` : Filtrer par le département.

2. **`doc_type`**  
   - Permet de filtrer le périmètre par type de procédure :
     - `CC`
     - `PLU`
     - `SCOT`

---

### Format de la réponse

La réponse est une liste d'objets, chaque objet représentant un périmètre avec les attributs suivants :

```json
{
  "id": "Identifiant unique du périmètre", // String
  "created_at": "Date de création du périmètre (ISO)", // String
  "added_at": "Date d'ajout du périmètre (ISO)", // String
  "collectivite_code": "Code INSEE de la collectivité associée", // String
  "collectivite_type": "Type de la collectivité associée", // String
  "procedure_id": "Identifiant de la procédure liée", // String
  "opposable": "Indique si le périmètre est opposable", // Boolean
  "departement": "Département du périmètre", // String
}
