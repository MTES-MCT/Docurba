<template>
  <GeoIDECardList
    v-if="!loading && towns"
    :cards="dataset"
    :region="regionISO"
    :themes="themes"
  />
  <VGlobalLoader v-else />
</template>

<script>
export default {
  props: {
    territorialAuthority: {
      required: true,
      type: Object
    },
    towns: {
      required: true,
      type: Array
    }
  },
  data () {
    return {
      dataset: [],
      loading: true,
      regionISO: null,
      themes: []
    }
  },
  watch: {
    territorialAuthority: {
      async handler (value) {
        this.regionISO = (await this.$regionApi.get(value.regionCode))?.iso || null
      },
      immediate: true
    }
  },
  async mounted () {
    this.towns.forEach((town) => {
      this.$matomo([
        'trackEvent',
        'Socle de PAC',
        'GeoIDE',
        `${this.$route.query.document} - ${town.code}`
      ])
    })

    const parsedInseeCode = this.towns.map(town => `commune/${town.code}`)
    const { cards, themes } = await this.$daturba.getGeoIDE(parsedInseeCode.join(' or '))
    this.dataset = cards
    const inspireThemes = themes.dimension.find(d => d['@label'] === 'inspireThemes')

    if (inspireThemes && inspireThemes.category) {
      this.themes = inspireThemes.category.map((c) => {
        return {
          id: c['@value'],
          text: `${c['@label']} (${c['@count']})`
        }
      })
    } else {
      this.themes = []
    }

    this.loading = false
  }
}
</script>
