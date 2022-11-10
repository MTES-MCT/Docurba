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
      <v-spacer />
      <OnboardingPacDialog />
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
        { text: 'Socle du PAC', to: '/pacsec/content' },
        { text: 'Base territoriale', to: '/pacsec/data' },
        { text: 'Géo-IDE', to: '/pacsec/geoide' },
        { text: 'Ressources', to: '/pacsec/ressources' },
        { text: 'Glossaire', to: '/pacsec/glossaire' }
      ]
    }
  }
}
</script>
