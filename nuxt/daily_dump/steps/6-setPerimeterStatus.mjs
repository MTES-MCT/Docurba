import { appendToGithubSummary } from '../common.mjs'
import departements from '../miscs/referentiels/departements.json' assert { type: 'json' }

async function updatePerimeterStatus(config) {
  for (const departement of departements) {
    console.log(`Updating ${departement.code} ${departement.intitule}`)
    console.time(departement.code)
    const response = await fetch(
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
