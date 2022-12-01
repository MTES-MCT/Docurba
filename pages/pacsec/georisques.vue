<template>
  <GeoIDECardList v-if="!loading" :region="currentRegion" :cards="dataset" :themes="[]" />
  <VGlobalLoader v-else />
</template>

<script>
export default {
  data () {
    return {
      dataset: [],
      themes: [],
      loading: true
    }
  },
  computed: {
    currentRegion () {
      return this.$route.query.region
    }
  },
  async mounted () {
    // Start Analytics
    const inseeQuery = this.$route.query.insee
    const codes = typeof (inseeQuery) === 'object' ? inseeQuery : [inseeQuery]

    if (codes) {
      codes.forEach((code) => {
        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Georisques',
          `${this.$route.query.document} - ${code}`
        ])
      })
    }
    // End Analytics

    // const parsedInseeCode = codes.map((code) => {
    //   return `commune/${code.toString().length < 5 ? '0' + code : code}`
    // })

    // console.log('CODE: ', parsedInseeCode)

    function objToArr (obj) {
      const arr = []
      for (const [key, value] of Object.entries(obj)) {
        console.log(`${key}: ${value}`)
        arr.push({ nom: key, valeur: value })
      }
      return arr
    }

    const data = await this.$daturba.getGeorisques({ dataset: 'zonage_sismique', insee: '74001' })
    console.log('Data Georisques: ', data)
    this.dataset = [data].map(e => ({ champs: objToArr(data.data[0]), title: data.dataset }))

    // const inspireThemes = themes.dimension.find(d => d['@label'] === 'inspireThemes')

    // if (inspireThemes && inspireThemes.category) {
    //   this.themes = inspireThemes.category.map((c) => {
    //     return {
    //       text: `${c['@label']} (${c['@count']})`,
    //       id: c['@value']
    //     }
    //   })
    // } else {
    //   this.themes = []
    // }

    this.loading = false
  }
}
</script>
