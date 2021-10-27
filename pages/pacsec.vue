<template>
  <v-container fluid>
    <v-tabs show-arrows>
      <v-tab
        v-for="tab in tabs"
        :key="tab.text"
        :to="{path: tab.to, query: $route.query}"
        nuxt
      >
        {{ tab.text }}
      </v-tab>
    </v-tabs>
    <NuxtChild />
  </v-container>
</template>

<script>

export default {
  name: 'PACsec',
  data () {
    return {
      tabs: [
        { text: 'PAC sec', to: '/pacsec/content' },
        { text: 'Jeux de données', to: '/pacsec/data' },
        { text: 'Ressources', to: '/pacsec/ressources' }
      ]
    }
  }
}
</script>
