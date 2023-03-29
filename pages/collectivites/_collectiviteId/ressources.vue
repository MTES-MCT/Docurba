<template>
  <v-container>
    <v-row align="end">
      <v-col cols="auto">
        <h2>Ressources</h2>
      </v-col>
      <v-col>
        <DashboardCollectivitesInnerNav :is-epci="isEpci" :collectivite="collectivite" :communes="communes" :region="region" />
      </v-col>
    </v-row>
    <RessourcesList :ressources="ressources" />
  </v-container>
</template>

<script>
import RessourcesList from '@/components/Ressources/RessourcesList.vue'

export default {
  components: {
    RessourcesList
  },
  async asyncData ({ $content }) {
    const ressources = await $content('Ressources', {
      deep: true
    }).fetch()

    return {
      ressources
    }
  },
  mounted () {
    // Start Analytics
    const inseeQuery = this.$route.query.insee
    const codes = typeof (inseeQuery) === 'object' ? inseeQuery : [inseeQuery]

    if (codes) {
      codes.forEach((code) => {
        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Ressources',
          `${this.$route.query.document} - ${code}`
        ])
      })
    }
    // End Analytics
  }
}
</script>
