
const _ = require('lodash')
const { topology } = require('topojson-server')

const communes = require('../Data/EnrichedCommunes.json')
const intercommunalites = require('../Data/EnrichedIntercommunalites.json')

const departements = require('../Data/INSEE/departements.json')
const regions = require('../Data/INSEE/regions.json')

const geojsonCommunes = require('../Data/communes-france-geo.json')

const convertArrayToObject = (array, key) => {
  const initialValue = {}
  return array.reduce((obj, item) => {
    return {
      ...obj,
      [item[key]]: item
    }
  }, initialValue)
}

module.exports = {
  getCollectivite (code) {
    return code.length > 5 ? this.getIntercommunalite(code) : this.getCommune(code)
  },
  getCollectivites (codes) {
    const communes = this.getCommunes({ codes })
    const intercommunalites = this.getIntercommunalites({ codes })
    return [...communes, ...intercommunalites]
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
  },
  getCommuneGeoJSON (codeInsee) {
    const commune = geojsonCommunes.features.find(feat => feat.id === codeInsee)
    if (!commune) { throw new Error(`Code INSEE ${codeInsee} invalide`) }
    return commune
  },
  getCommunesGeoJSON (codesInsee) {
    const codes = Array.isArray(codesInsee) ? codesInsee : [codesInsee]

    return {
      type: 'FeatureCollection',
      features: codes.map(code => this.getCommuneGeoJSON(code))
    }
  },
  getCommunesTopoJSON (codesInsee) {
    const codes = Array.isArray(codesInsee) ? codesInsee : [codesInsee]

    const communes = codes.map(code => this.getCommuneGeoJSON(code))
    return topology(convertArrayToObject(communes, 'id'))
  }
}
