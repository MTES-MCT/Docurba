<template>
  <GeoIDECardList v-if="!loading && communes" :region="region.iso" :cards="dataset" :themes="themes" />
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
    },
    region: {
      type: Object,
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
      const parsedInseeCode = this.communes.map(commune => `commune/${commune.id}`)
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
