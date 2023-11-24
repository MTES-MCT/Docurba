<template>
  <!-- TODO Pour l'instant, un composant spécifique à GeoBretagne -->
  <GeoBretagneViewer v-if="collectivite.region.iso === 'FR-BRE'" :collectivite-code="collectivite.code" :is-epci="isEpci" class="mt-4" />
  <DataSourcesList v-else-if="!loading && communes" :region="collectivite.region.iso" :data-sources="dataset" :themes="themes" />
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
        return c.code
      })
      : this.collectivite.code

    if (this.collectivite.region.iso !== 'FR-BRE') {
      const { dataset, themes } = await this.$daturba.getData(this.collectivite.region.iso, collectiviteId)
      this.dataset = dataset
      this.themes = themes
    }

    this.loading = false
  }
}
</script>
