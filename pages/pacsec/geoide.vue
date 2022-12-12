<template>
  <GeoIDECardList v-if="!loading && $route.query.insee" :region="currentRegion" :cards="dataset" :themes="themes" />
  <v-container v-else-if="!loading" class="fill-height">
    <v-row class="fill-height" justify="center" align="center">
      <v-col cols="12">
        <v-card rounded="lg" class="pa-6">
          <v-card-text>
            <LandingSearchForm path="/pacsec/geoide" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
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
  watch: {
    '$route.query.insee' () {
      this.fetchDatasets()
    }
  },
  async mounted () {
    if (this.$route.query.insee) {
      const inseeQuery = this.$route.query.insee
      const codes = typeof (inseeQuery) === 'object' ? inseeQuery : [inseeQuery]

      // Start Analytics
      if (codes) {
        codes.forEach((code) => {
          this.$matomo([
            'trackEvent', 'Socle de PAC', 'GeoIDE',
          `${this.$route.query.document} - ${code}`
          ])
        })
      }
      // End Analytics

      await this.fetchDatasets()
    }

    this.loading = false
  },
  methods: {
    async fetchDatasets () {
      this.loading = true
      const inseeQuery = this.$route.query.insee
      const codes = typeof (inseeQuery) === 'object' ? inseeQuery : [inseeQuery]

      const parsedInseeCode = codes.map((code) => {
        return `commune/${code.toString().length < 5 ? '0' + code : code}`
      })

      const { cards, themes } = await this.$daturba.getGeoIDE(parsedInseeCode.join(' or '))

      this.dataset = cards

      const inspireThemes = themes.dimension.find(d => d['@label'] === 'inspireThemes')

      if (inspireThemes && inspireThemes.category) {
        this.themes = inspireThemes.category.map((c) => {
          return {
            text: `${c['@label']} (${c['@count']})`,
            id: c['@value']
          }
        })
      } else {
        this.themes = []
      }

      this.loading = false
    }
  }
}
</script>
