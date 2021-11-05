<template>
  <LayoutsCustomApp extended-app-bar>
    <template #headerExtension>
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
    </template>
    <NuxtChild />
  </LayoutsCustomApp>
</template>

<script>

export default {
  name: 'PACsec',
  layout: 'app',
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
