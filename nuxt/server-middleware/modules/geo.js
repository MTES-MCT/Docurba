
const _ = require('lodash')
const { topology } = require('topojson-server')
const { center } = require('@turf/turf')

const communes = require('../Data/referentiels/communes.json')
const intercommunalites = require('../Data/referentiels/groupements.json')

const departements = require('../Data/INSEE/departements.json')
const regions = require('../Data/INSEE/regions.json')

// const geojsonCommunes = require('../Data/communes-france-geo.json')
const geojsonCommunes = require('../Data/geojson/communes-geo.json')
const geojsonIntercommunalites = require('../Data/geojson/epci-geo.json')
const geojsonDepartements = require('../Data/geojson/departements-geo.json')
const geojsonRegions = require('../Data/geojson/regions-geo.json')
const topojsonFrance = require('../Data/geojson/france-topo.json')


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
  getGeometries (communeCodes = [], departementCodes = [], regionCodes = [], addDepReg = true, format = 'geojson') {
    const comFeatures = []
    const depFeatures = []
    const regFeatures = []

    for (const com of communeCodes) {
      const feature = geojsonCommunes.features.find(feat => feat.properties.com === com)
      comFeatures.push(feature)

      if (addDepReg && !departementCodes.includes(feature.properties.dep)) {
        departementCodes.push(feature.properties.dep)
      }
    }

    for (const dep of departementCodes) {
      const feature = geojsonDepartements.features.find(feat => feat.properties.dep === dep)
      depFeatures.push(feature)

      if (addDepReg && !regionCodes.includes(feature.properties.reg)) {
        regionCodes.push(feature.properties.reg)
      }
    }

    for (const reg of regionCodes) {
      const feature = geojsonRegions.features.find(feat => feat.properties.reg === reg)
      regFeatures.push(feature)
    }

    if (format === 'geojson') {
      return {
        type: 'FeatureCollection',
        features: [
          ...comFeatures,
          ...depFeatures,
          ...regFeatures
        ]
      }
    }

    if (format === 'topojson') {
      return topology({
        communes: { type: 'FeatureCollection', features: comFeatures },
        departements: { type: 'FeatureCollection', features: depFeatures },
        regions: { type: 'FeatureCollection', features: regFeatures }
      })
    }

    throw new Error('Format inconnu')
  },
  getCommunesGeoJson (codes = [], addDepReg = true) {
    if (!codes?.length) {
      return topojsonFrance
    }
    const communeCodes = Array.isArray(codes) ? codes : [codes]
    return this.getGeometries(communeCodes, [], [], addDepReg, 'geojson')
  },
  getCommunesTopoJson (codes = [], addDepReg = true) {
    const communeCodes = Array.isArray(codes) ? codes : [codes]
    return this.getGeometries(communeCodes, [], [], addDepReg, 'topojson')
  },
  getDepartementsGeoJson (codes = [], addReg = true) {
    const departementCodes = Array.isArray(codes) ? codes : [codes]
    return this.getGeometries([], departementCodes, [], addReg, 'geojson')
  },
  getDepartementsTopoJson (codes = [], addReg = true) {
    const departementCodes = Array.isArray(codes) ? codes : [codes]
    return this.getGeometries([], departementCodes, [], addReg, 'topojson')
  },
  getRegionsGeoJson (codes = []) {
    const regionCodes = Array.isArray(codes) ? codes : [codes]
    return this.getGeometries([], [], regionCodes, false, 'geojson')
  },
  getRegionsTopoJson (codes = []) {
    const regionsCodes = Array.isArray(codes) ? codes : [codes]
    return this.getGeometries([], [], regionsCodes, false, 'topojson')
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
