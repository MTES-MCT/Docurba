
const _ = require('lodash')

const communes = require('./Data/EnrichedCommunes.json')
const intercommunalites = require('./Data/EnrichedIntercommunalites.json')

const departements = require('./Data/INSEE/departements.json')
const regions = require('./Data/INSEE/regions.json')

module.exports = {
  getCommunes (query) {
    const queryKeys = Object.keys(query)

    if (query.codes) {
      const communesCodes = query.codes

      const filterredCommunes = communes.filter((commune) => {
        return communesCodes.includes(commune.code)
      })

      return filterredCommunes
    }

    if (queryKeys.length) {
      const filterredCommunes = _.filter(communes, query)
      return filterredCommunes
    } else {
      return communes
    }
  },
  getCommune (codeInsee) {
    const commune = communes.find((c) => {
      return c.code === codeInsee
    })

    if (commune) {
      const departement = Object.assign({}, departements.find(d => d.code === commune.departementCode))
      delete departement.communes
      delete departement.region

      return Object.assign({
        intercommunalite: intercommunalites.find(i => i.code === commune.intercommunaliteCode),
        region: regions.find(r => r.code === commune.regionCode),
        departement
      }, commune)
    } else {
      return null
    }
  },
  getIntercommunalites (query) {
    const queryKeys = Object.keys(query)

    if (query.codes) {
      const intercommunalitesCodes = query.codes

      const filterredIntercomunalites = intercommunalites.filter((intercommunalite) => {
        return intercommunalitesCodes.includes(intercommunalite.code)
      })

      return filterredIntercomunalites
    }

    if (queryKeys.length) {
      const filterredIntercomunalites = _.filter(intercommunalites, query)
      return filterredIntercomunalites
    } else {
      return intercommunalites
    }
  },
  getIntercommunalite (codeSiren) {
    const intercommunalite = intercommunalites.find((c) => {
      return c.code === codeSiren
    })

    if (intercommunalite) {
      const departement = Object.assign({}, departements.find(d => d.code === intercommunalite.departementCode))
      delete departement.communes
      delete departement.region

      return Object.assign({
        region: regions.find(r => r.code === intercommunalite.regionCode),
        departement
      }, intercommunalite)
    } else {
      return null
    }
  }
}
