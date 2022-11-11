import axios from 'axios'

const geoIde = axios.create({
  baseURL: 'http://catalogue.geo-ide.developpement-durable.gouv.fr'
})

const geoIdeParams = {
  _content_type: 'json',
  resultType: 'details',
  fast: 'index'
}

export default ({ route }, inject) => {
  const sourceMap = {
    'FR-ARA': {
      url: 'https://catalogue.datara.gouv.fr/base_territoriale/results?_format=json',
      themesUrl: 'https://catalogue.datara.gouv.fr/base_territoriale/themes',
      data: {
        limit: -1,
        list: false,
        offset: 0,
        'themes[]': ['2', '3', '4', '5', '6', '7', '8', '10', '11', '12', '132', '14', '15', '16', '17', '18', '27', '28', '29', '30', '31', '32', '33', '35', '36', '37', '38', '39', '40', '41', '42', '43', '45', '46', '47', '48', '56', '57', '58', '59', '60', '61', '62', '63', '64', '77', '78', '79', '80', '130', '131', '93', '94', '95', '96', '97', '98', '99', '100', '101', '102', '103', '105', '106', '108', '128', '120', '121', '122', '123', '125'],
        type: 'pac'
      }
    },
    'FR-PDL': {
      url: 'https://catalogue.sigloire.fr/base_territoriale/results?_format=json',
      themesUrl: 'https://catalogue.sigloire.fr/base_territoriale/themes',
      data: {
        limit: -1,
        list: false,
        offset: 0,
        'themes[]': ['5', '6', '7', '8', '60', '10', '11', '25', '24', '41', '42', '9', '12', '26', '61', '63', '47', '48', '49', '15', '16', '27', '17', '45', '31', '32', '33', '34', '35', '14', '23', '22', '28', '30', '46', '36', '37', '38', '39', '40']
        // 'themes[]': ['6', '7', '60', '11', '25', '24', '42', '12', '26', '63', '48', '49', '16', '27', '17', '45', '32', '33', '34', '35', '30', '46', '23', '22', '37', '38', '39', '40']
      }
    },
    'FR-OCC': {
      url: 'https://catalogue.picto-occitanie.fr/base_territoriale/results',
      themesUrl: 'https://catalogue.picto-occitanie.fr/base_territoriale/themes',
      data: {
        limit: -1,
        list: false,
        offset: 0,
        'themes[]': ['42', '43', '44', '195', '170', '47', '40', '41', '228', '189', '196', '107', '108', '109', '117', '118', '119', '120', '121', '122', '124', '125', '128', '129', '130', '131', '132', '231', '247', '137', '138', '139', '140', '141', '142', '232', '144', '145', '240', '241', '147', '148', '175', '150', '151', '156', '157', '158', '159', '178', '161', '234', '252', '250', '207', '58', '48', '66', '79', '200', '201', '251', '39', '57', '183', '85', '86', '112', '68', '152', '153', '168', '229', '197', '235', '237', '238', '99', '102', '113', '114', '239', '116', '154', '155', '123', '211', '198', '202', '203', '236', '190', '191', '218', '222', '171', '199', '248', '209', '63', '71', '72', '73', '74', '204', '76', '78', '77', '180', '83', '84', '87', '88', '89', '213', '214', '163', '164', '165', '166', '184', '185', '186', '187', '210', '212', '90', '101', '91', '92', '94', '95', '96', '98', '111', '167', '103', '104', '105', '106']
        // 'themes[]': ['5', '6', '7', '8', '60', '10', '11', '25', '24', '41', '42', '9', '12', '26', '61', '63', '47', '48', '49', '15', '16', '27', '17', '45', '31', '32', '33', '34', '35', '14', '23', '22', '28', '30', '46', '36', '37', '38', '39', '40']
        // 'themes[]': ['6', '7', '60', '11', '25', '24', '42', '12', '26', '63', '48', '49', '16', '27', '17', '45', '32', '33', '34', '35', '30', '46', '23', '22', '37', '38', '39', '40']
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
        mainLinkType: 'iframe'
      }
    })
  }

  const parsers = {
    'FR-ARA': prodigeParser,
    'FR-PDL': prodigeParser
  }

  const cardSourceUrl = {
    'FR-ARA' (cardData) {
      return `https://catalogue.datara.gouv.fr/base_territoriale/fiche?_format=json&id=${cardData.id}&nom_table=${cardData.nom_table}`
    },
    'FR-PDL' (cardData) {
      return `https://catalogue.sigloire.fr/base_territoriale/fiche?_format=json&id=${cardData.id}&nom_table=${cardData.nom_table}`
    }
  }

  const cardSourceMap = {
    async 'FR-ARA' (cardData) {
      const { data } = await axios({
        url: cardSourceUrl['FR-ARA'](cardData),
        method: 'get'
      })

      return data
    },
    async 'FR-PDL' (cardData) {
      const { data } = await axios({
        url: cardSourceUrl['FR-PDL'](cardData),
        method: 'get'
      })

      return data
    }
  }

  inject('daturba', {
    // search arg should be `commune/${codeInsee}` or `departement/${codeDepartement}` or `region/${codeRegion}`
    async getGeoIDE (search) {
      const { data } = await geoIde({
        method: 'get',
        url: '/catalogue/srv/eng/q',
        params: Object.assign({ any: search }, geoIdeParams)
      })

      const { metadata, summary } = data
      let cards = []

      if (metadata) {
        cards = metadata.map((dataset) => {
          const rawLinks = typeof (dataset.link) === 'object' ? dataset.link : [dataset.link]
          const links = rawLinks.map((link) => {
            const vals = link.split('||')
            return {
              text: vals[0],
              url: vals[1]
            }
          })

          const datasetId = dataset['geonet:info'].uuid

          return {
            title: dataset.defaultTitle,
            tags: ['Géo-IDE'],
            text: dataset.abstract,
            links,
            mainLink: `http://catalogue.geo-ide.developpement-durable.gouv.fr/catalogue/srv/fre/catalog.search#/metadata/${datasetId}`,
            mainLinkType: 'link',
            categs: typeof (dataset.inspirethemewithac) === 'object' ? dataset.inspirethemewithac : [dataset.inspirethemewithac]
          }
        })
      }

      return { cards, themes: summary }
    },
    getCardDataUrl (region = route.query.region, data) {
      return cardSourceUrl[region](data)
    },
    getCardData (region = route.query.region, data) {
      return cardSourceMap[region](data)
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
          url: source.url,
          method: 'post',
          data: Object.assign({
            'insee[]': parsedInseeCode
          }, source.data)
        })

        const { data: themes } = await axios({
          url: source.themesUrl,
          method: 'get'
        })

        // console.log('getData', region, dataset, themes)

        dataset.forEach((data) => {
          parsers[region](data, themes)
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
