<template>
  <!-- TODO Pour l'instant, un composant spécifique à GeoBretagne -->
  <GeoBretagneViewer v-if="collectivite.region.iso === 'FR-BRE'" :collectivite-code="collectivite.code" :is-epci="isEpci" class="mt-4" />
  <DataSourcesList v-else-if="communes" :region="collectivite.region.iso" :collectivites-codes="collectivitesCodes" />
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
      collectivitesCodes: []
    }
  },
  created () {
    // Start Analytics
    this.communes.forEach((commune) => {
      this.$matomo([
        'trackEvent', 'Socle de PAC', 'Data',
    `${this.$route.query.document} - ${commune}`
      ])
    })
    // End Analytics

    this.collectivitesCodes = this.isEpci
      ? this.communes.map((c) => {
        return c.code
      })
      : [this.collectivite.code]
  }
}
</script>
