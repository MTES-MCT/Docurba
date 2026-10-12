<template>
  <!-- TODO Pour l'instant, un composant spécifique à GeoBretagne -->
  <GeoBretagneViewer
    v-if="territorialAuthority.regionCode === '53'"
    :collectivite-code="territorialAuthority.code"
    :is-epci="!territorialAuthority.intermunicipalityCode"
  />
  <DataSourcesList
    v-else-if="towns"
    :region="territorialAuthority.regionCode"
    :collectivites-codes="townCodes"
    :default-selected-theme="defaultSelectedTheme"
    @select-theme="selectTheme($event)"
  />
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
  computed: {
    defaultSelectedTheme () {
      return this.$route.query.theme ? Number(this.$route.query.theme) : null
    },
    townCodes () {
      return this.towns.map(({ code }) => code)
    }
  },
  mounted () {
    this.townCodes.forEach((townCode) => {
      this.$matomo([
        'trackEvent',
        'Socle de PAC',
        'Data',
        `${this.$route.query.document} - ${townCode}`
      ])
    })
  },
  methods: {
    selectTheme (themeId) {
      this.$router.replace({
        query: {
          ...this.$route.query,
          theme: themeId
        }
      })
    }
  }
}
</script>
