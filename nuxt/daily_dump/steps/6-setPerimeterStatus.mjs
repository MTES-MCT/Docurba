import { appendToGithubSummary } from '../common.mjs'
import departements from '../miscs/referentiels/departements.json' assert { type: 'json' }

async function updatePerimeterStatus(config) {
  for (const departement of departements) {
    console.log(`Updating ${departement.code} ${departement.intitule}`)
    console.time(departement.code)
    const response = await fetch(
      // Domaine hardcodé car action effectuée uniquement vers la production par Github Action
      // https://github.com/MTES-MCT/Docurba/pull/1539/commits/d687eb2fa9f9e5fc09106693f906b5f4fb6fc40e#r2436142963
      `https://nuxt3.docurba.incubateur.net/api/urba/procedures/perimetres/update?departementCode=${departement.code}`
    )
    if (!response.ok) {
      console.error(await response.text())
      appendToGithubSummary(
        `Erreur lors de la mise à jour des statuts de ${departement.intitule} (${departement.code})`
      )
    }
    console.timeEnd(departement.code)
  }
}

export { updatePerimeterStatus }
