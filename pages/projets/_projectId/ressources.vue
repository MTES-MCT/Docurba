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
    // Start Analytics
    // No project yep on this page yet.
    // this.$matomo([
    //   'trackEvent', 'Projet PAC', 'Data',
    //     `${this.project.doc_type} - ${this.project.epci ? this.project.epci.label : this.project.towns[0].nom_commune}`
    // ])
    // End Analytics
  }
}
</script>
