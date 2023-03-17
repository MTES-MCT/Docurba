<template>
  <v-container>
    <v-row align="end">
      <v-col cols="auto">
        <h2>Données</h2>
      </v-col>
      <v-col>
        <DashboardCollectivitesInnerNav />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-tabs>
          <v-tab
            v-for="tab in tabs"
            :key="tab.text"
            :to="{name: tab.to, query: $route.query}"
            nuxt
          >
            {{ tab.text }}
          </v-tab>
        </v-tabs>
      </v-col>
    </v-row>
    <NuxtChild :is-epci="isEpci" :collectivite="collectivite" />
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
    }
  },
  data () {
    return {
      tabs: [
        { text: 'Base territoriale', to: 'dashboard-collectivites-collectiviteId-index-donnees-data' },
        { text: 'Géo-IDE', to: 'dashboard-collectivites-collectiviteId-index-donnees-geoide' },
        { text: 'Géorisques', to: 'dashboard-collectivites-collectiviteId-index-donnees-georisques' },
        { text: 'INPN', to: 'dashboard-collectivites-collectiviteId-index-donnees-inpn' }
      ]
    }
  }
  // mounted () {
  //   if (this.$route.query.region === 'FR-BRE') {
  //     this.tabs.splice(2, 0, { text: 'GéoBretagne', to: '/pacsec/geobretagne' })
  //     this.tabs = this.tabs.filter(e => e.to !== '/pacsec/data')
  //   }
  // }
}
</script>
