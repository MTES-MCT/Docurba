<template>
  <v-container>
    <v-row align="end">
      <v-col cols="auto">
        <h2>Données</h2>
      </v-col>
      <v-col>
        <DashboardCollectivitesInnerNav :is-epci="isEpci" :collectivite="collectivite" :communes="communes" />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-tabs>
          <v-tab
            v-for="tab in tabs"
            :key="tab.text"
            v-model="currTab"
            :to="{path: tab.path, query: $route.query}"
            nuxt
          >
            {{ tab.text }}
          </v-tab>
        </v-tabs>
      </v-col>
    </v-row>
    <NuxtChild :is-epci="isEpci" :collectivite="collectivite" :communes="communes" />
  </v-container>
</template>

<script>

export default {
  name: 'PACsec',
  layout: 'app',
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
      currTab: 0,
      tabs: [
        { text: 'Base territoriale', path: `/collectivites/${this.$route.params.collectiviteId}/donnees/data` },
        { text: 'Géo-IDE', path: `/collectivites/${this.$route.params.collectiviteId}/donnees/geoide` },
        { text: 'Géorisques', path: `/collectivites/${this.$route.params.collectiviteId}/donnees/georisques` },
        { text: 'INPN', path: `/collectivites/${this.$route.params.collectiviteId}/donnees/inpn` },
        { text: 'GPU', path: `/collectivites/${this.$route.params.collectiviteId}/donnees/gpu` }
      ]
    }
  }

}
</script>
