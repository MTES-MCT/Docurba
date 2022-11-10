<template>
  <GeoIDECardList v-if="!loading" :region="currentRegion" :cards="dataset" :themes="themes" />
  <VGlobalLoader v-else />
</template>

<script>
export default {
  // async asyncData ({ $daturba, route }) {
  //   return await $daturba.getData(route.query.region, route.query.insee)
  // },
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
          'trackEvent', 'Socle de PAC', 'GeoIDE',
          `${this.$route.query.document} - ${code}`
        ])
      })
    }
    // End Analytics

    const parsedInseeCode = codes.map((code) => {
      return `commune/${code.toString().length < 5 ? '0' + code : code}`
    })

    const { cards, themes } = await this.$daturba.getGeoIDE(parsedInseeCode.join(' or '))

    this.dataset = cards

    this.themes = themes.dimension.find(d => d['@label'] === 'inspireThemes').category.map((c) => {
      return {
        text: `${c['@label']} (${c['@count']})`,
        id: c['@value']
      }
    })

    this.loading = false
  }
}
</script>
