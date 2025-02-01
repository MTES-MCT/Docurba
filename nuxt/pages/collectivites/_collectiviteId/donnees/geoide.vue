<template>
  <GeoIDECardList v-if="!loading && communes" :region="collectivite.region.iso" :cards="dataset" :themes="themes" />
  <VGlobalLoader v-else />
</template>

<script>

export default {
  name: 'GeoIDE',
  props: {
    isEpci: {
      type: Boolean,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    },
    communes: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      dataset: [],
      themes: [],
      loading: true
    }
  },
  async mounted () {
    this.communes.forEach((commune) => {
      this.$matomo([
        'trackEvent', 'Socle de PAC', 'GeoIDE',
        `${this.$route.query.document} - ${commune.id}`
      ])
    })

    await this.fetchDatasets()

    this.loading = false
  },
  methods: {
    async fetchDatasets () {
      this.loading = true
      const parsedInseeCode = this.communes.map(commune => `commune/${commune.code}`)
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
