<template>
  <v-container>
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
    if (this.$route.query.insee) {
      this.$route.query.insee.forEach((code) => {
        this.$matomo.trackEvent('Socle de PAC', 'Ressources', `${this.$route.query.document} - ${code}`)
      })
    }
  }
}
</script>
