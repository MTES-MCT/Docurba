<template>
  <DataSourcesList v-if="!loading && communes" :region="region.iso" :data-sources="dataset" :themes="themes" />
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
  name: 'BaseTerritoriale',
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
    // Start Analytics
    this.communes.forEach((commune) => {
      this.$matomo([
        'trackEvent', 'Socle de PAC', 'Data',
    `${this.$route.query.document} - ${commune}`
      ])
    })
    // End Analytics

    const collectiviteId = this.isEpci
      ? this.communes.map((c) => {
        return c.code_commune_INSEE
      })
      : this.collectivite.id

    console.log('collectiviteId', collectiviteId)

    const { dataset, themes } = await this.$daturba.getData(this.region.iso, collectiviteId)

    this.dataset = dataset
    this.themes = themes

    this.loading = false
  }
}
</script>
