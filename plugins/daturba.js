import axios from 'axios'

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
    }
  }

  const parsers = {
    'FR-ARA' (data, themes) {
      data.objets.forEach((obj) => {
        obj.nom_table = data.nom_table
      })

      data.theme = themes.find((theme) => {
        const dataTheme = theme.children.find((subTheme) => {
          return subTheme.id === data.theme
        })

        if (dataTheme) {
          data.subTheme = dataTheme
        }

        return !!dataTheme
      })
    }
  }

  const cardSourceMap = {
    async 'FR-ARA' (cardData) {
      const { data } = await axios({
        url: `https://catalogue.datara.gouv.fr/base_territoriale/fiche?_format=json&id=${cardData.id}&nom_table=${cardData.nom_table}`,
        method: 'get'
      })

      console.log(data)

      return data
    }
  }

  inject('daturba', {
    getCardData (region = route.query.region, data) {
      return cardSourceMap[region](data)
    },
    async getData (region = route.query.region, inseeCodes = route.query.insee) {
      const source = sourceMap[region]
      const parsedInseeCode = inseeCodes.map((code) => {
        return code.toString().length < 5 ? '0' + code : code
      })

      if (source) {
        const dataset = (await axios({
          url: source.url,
          method: 'post',
          data: Object.assign({
            'insee[]': parsedInseeCode
          }, source.data)
        })).data

        const themes = (await axios({
          url: source.themesUrl,
          method: 'get'
        })).data

        // console.log(dataset.length)

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
