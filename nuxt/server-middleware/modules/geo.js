
const _ = require('lodash')
const { center } = require('@turf/turf')

const communes = require('../Data/referentiels/communes.json')
const intercommunalites = require('../Data/referentiels/groupements.json') // Why this is not groupements_2024.json? Mystery.

const departements = require('../Data/INSEE/departements.json')
const regions = require('../Data/INSEE/regions.json')

const geojsonCommunes = require('../Data/geojson/communes-geo.json')
const geojsonIntercommunalites = require('../Data/geojson/epci-geo.json')


module.exports = {
  getCollectivite (code) {
    return code.length > 5 ? this.getIntercommunalite(code) : this.getCommune(code)
  },
  getCollectivites ({ codes, departements }) {
    // console.log('getCollectivites: ')
    if (codes) {
      const communes = this.getCommunes({ codes })
      const intercommunalites = this.getIntercommunalites({ codes })
      return [...communes, ...intercommunalites]
    }
  },
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
  getMembersOfMembers (intercommunalite) {
    intercommunalite.membres.forEach((membre) => {
      if (membre.code.length > 5) {
        const interco = this.getIntercommunalite(membre.code)
        if (interco) {
          intercommunalite.membres.push(...interco.membres)
        }
      }
    })
  },
  getIntercommunalite (codeSiren) {
    const intercommunalite = intercommunalites.find((c) => {
      return c.code === codeSiren
    })

    if (intercommunalite) {
      this.getMembersOfMembers(intercommunalite)

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
  },
  getCommuneCenter (code) {
    const feature = geojsonCommunes.features.find(feat => feat.properties.com === code)
    if (!feature) {
      throw new Error('Commune introuvable')
    }
    return center(feature).geometry
  },
  getIntercommunaliteCenter (code) {
    const feature = geojsonIntercommunalites.features.find(feat => feat.properties.epci === code)
    if (!feature) {
      throw new Error('EPCI introuvable')
    }
    return center(feature).geometry
  }
}
