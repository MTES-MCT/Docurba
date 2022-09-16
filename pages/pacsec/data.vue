<template>
  <DataSourcesList v-if="!loading" :region="currentRegion" :data-sources="dataset" :themes="themes" />
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
    if (this.$route.query.insee) {
      this.$route.query.insee.forEach((code) => {
        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Data',
          `${this.$route.query.document} - ${code}`
        ])
      })
    }

    const { dataset, themes } = await this.$daturba.getData(this.$route.query.region, this.$route.query.insee)

    this.dataset = dataset
    this.themes = themes
    this.loading = false
  }
}
</script>
