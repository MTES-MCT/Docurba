<template>
  <v-container>
    <RessourcesList :ressources="ressources" />
  </v-container>
</template>

<script>
import RessourcesList from '@/components/Ressources.vue/RessourcesList.vue'

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
  }
}
</script>
