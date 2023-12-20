<template>
  <GeoIDECardList v-if="!loading" :region="currentRegion" :cards="dataset" :themes="themes" />
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
    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
    this.project = projects ? projects[0] : null

    // Start Analytics
    this.$matomo([
      'trackEvent', 'Projet PAC', 'GeoIde',
          `${this.project.doc_type} - ${this.project.epci ? this.project.epci.intitule : this.project.towns[0].intitule}`
    ])
    // End Analytics

    if (this.project) {
      this.fetchDatasets()
    }

    // await this.fetchDatasets()

    this.loading = false
  },
  methods: {
    async fetchDatasets () {
      this.loading = true
      const codes = this.project.towns.map(t => t.code)

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
