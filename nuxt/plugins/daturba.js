import axios from 'axios'
import GEORISQUES_MAP from '@/assets/data/GeoRisquesMap.json'

export default ({ route }, inject) => {
  // MAP permet d'afficher les onglet de source
  const sourceMap = {
    // eslint-disable-next-line quote-props
    '84': {
      baseUrl: 'https://bdterr.open-datara.fr/base_territoriale',
      data: {
        limit: -1,
        list: false,
        offset: 0,
        'themes[]': ['2', '3', '4', '5', '6', '7', '8', '10', '11', '12', '132', '14', '15', '16', '17', '18', '27', '28', '29', '30', '31', '32', '33', '35', '36', '37', '38', '39', '40', '41', '42', '43', '45', '46', '47', '48', '56', '57', '58', '59', '60', '61', '62', '63', '64', '77', '78', '79', '80', '130', '131', '93', '94', '95', '96', '97', '98', '99', '100', '101', '102', '103', '105', '106', '108', '128', '120', '121', '122', '123', '125'],
        type: 'pac'
      }
    },

    // eslint-disable-next-line quote-props
    '52': {
      baseUrl: 'https://catalogue.sigloire.fr/base_territoriale',
      data: {
        limit: -1,
        list: false,
        offset: 0,
        'themes[]': ['5', '6', '7', '8', '60', '10', '11', '25', '24', '41', '42', '9', '12', '26', '61', '63', '47', '48', '49', '15', '16', '27', '17', '45', '31', '32', '33', '34', '35', '14', '23', '22', '28', '30', '46', '36', '37', '38', '39', '40']
      }
    }
  }

  function prodigeParser (data, themes) {
    data.theme = themes.find((theme) => {
      const dataTheme = theme.children.find((subTheme) => {
        return subTheme.id === data.theme
      })

      if (dataTheme) {
        data.subTheme = dataTheme
      }

      return !!dataTheme
    })

    data.objets.forEach((obj) => {
      obj.nom_table = data.nom_table

      obj.card = {
        title: obj.nom,
        tags: data.subTheme ? [data.subTheme.text] : [],
        links: obj.ressources.map((l) => {
          return {
            text: l.alias || l[0].alias,
            url: l.valeur || l[0].valeur
          }
        }),
        mainLink: obj.carto_url,
        mainLinkType: 'iframe',
        // Prodige Keys
        id: obj.id,
        nom_table: data.nom_table
      }
    })
  }

  inject('daturba', {
    async getCommunesDetails (inseeArr) {
      const { data } = await axios({
        url: '/api/communes',
        method: 'get',
        params: { communes: inseeArr }
      })
      return data
    },
    async getGeorisques ({ dataset, insee }) {
      const EXISTING_DATASETS = GEORISQUES_MAP.map(e => e.endpoint)
      if (!EXISTING_DATASETS.includes(dataset)) { throw new Error('Le dataset demandé est inconnu. Types disponibles:' + EXISTING_DATASETS.join(', ')) }
      // https://www.georisques.gouv.fr/api/v1/zonage_sismique?code_insee=74001&page=1&page_size=10&rayon=1000
      // TODO: ATTENTION, le max de join est de 10. Le faire autrement dans un cas de caumunauté de commune + grand
      // Ou le faire coté back ?
      if (Array.isArray(insee)) { insee = insee.join(',') }
      const { data } = await axios({
        url: '/api/georisques/q',
        method: 'get',
        params: { dataset, insee }
      })
      return { dataset, data: data.data }
    },
    // search arg should be `commune/${codeInsee}` or `departement/${codeDepartement}` or `region/${codeRegion}`
    async getGeoIDE (search, platform) {
      const { data } = await axios({
        url: '/api/geoide/q',
        method: 'get',
        params: { any: search, platform }
      })

      const { metadata, summary } = data
      let cards = []

      if (metadata) {
        cards = metadata.map((dataset) => {
          const rawLinks = typeof (dataset.link) === 'object' ? dataset.link : [dataset.link]
          const links = rawLinks.map((link) => {
            let vals = link.split('||')
            if (platform === 'bretagne') {
              vals = link.split('|')
              vals = [vals[1], vals[2]]
            }
            return {
              text: vals[0],
              url: vals[1]
            }
          })

          const datasetId = dataset['geonet:info'].uuid

          const PLATFORMS_MAP = {
            bretagne: {
              mainLink: 'https://geobretagne.fr/geonetwork',
              tags: ['GéoBretagne']
            },
            default: {
              mainLink: 'http://catalogue.geo-ide.developpement-durable.gouv.fr/catalogue',
              tags: ['Géo-IDE']
            }

          }
          const infosPlatform = PLATFORMS_MAP[platform] ?? PLATFORMS_MAP.default

          return {
            title: dataset.defaultTitle,
            tags: infosPlatform.tags,
            text: dataset.abstract,
            links,
            mainLink: `${infosPlatform.mainLink}/srv/fre/catalog.search#/metadata/${datasetId}`,
            mainLinkType: 'link',
            categs: typeof (dataset.inspirethemewithac) === 'object' ? dataset.inspirethemewithac : [dataset.inspirethemewithac]
          }
        })
      }

      return { cards, themes: summary }
    },
    getCardDataUrl (region = route.query.region, cardData) {
      return `${sourceMap[region].baseUrl}/fiche?_format=json&id=${cardData.id}&nom_table=${cardData.nom_table}`
    },
    async getCardData (region = route.query.region, cardData) {
      const { data } = await axios.get(this.getCardDataUrl(region, cardData))
      return data
    },
    async getData (region = route.query.region, inseeCodes = route.query.insee) {
      if (!region || !inseeCodes || !inseeCodes.length) { return {} }

      if (typeof (inseeCodes) !== 'object') { inseeCodes = [inseeCodes] }

      const source = sourceMap[region]
      const parsedInseeCode = inseeCodes.map((code) => {
        return code.toString().length < 5 ? '0' + code : code
      })

      if (source) {
        const { data: dataset } = await axios({
          url: source.baseUrl + '/results?_format=json',
          method: 'post',
          data: Object.assign({
            'insee[]': parsedInseeCode
          }, source.data)
        })

        const { data: themes } = await axios({
          url: source.baseUrl + '/themes',
          method: 'get'
        })

        dataset.forEach((data) => {
          prodigeParser(data, themes)
        })

        return {
          themes,
          dataset
        }
      } else {
        return {}
      }
    }
  })
}
