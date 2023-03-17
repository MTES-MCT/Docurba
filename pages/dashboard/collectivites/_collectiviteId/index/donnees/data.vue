<template>
  <DataSourcesList v-if="!loading && $route.query.insee" :region="currentRegion" :data-sources="dataset" :themes="themes" />
  <v-container v-else-if="!loading" class="fill-height">
    <v-row class="fill-height" justify="center" align="center">
      <v-col cols="12">
        <v-card rounded="lg" class="pa-6">
          <v-card-text>
            <LandingSearchForm path="/pacsec/data" />
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
  async mounted () {
    // Start Analytics
    const inseeQuery = this.$route.query.insee
    const codes = typeof (inseeQuery) === 'object' ? inseeQuery : [inseeQuery]

    if (codes) {
      codes.forEach((code) => {
        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Data',
    `${this.$route.query.document} - ${code}`
        ])
      })
    }
    // End Analytics

    const { dataset, themes } = await this.$daturba.getData(this.$route.query.region, this.$route.query.insee)

    this.dataset = dataset
    this.themes = themes

    this.loading = false
  }
}
</script>
