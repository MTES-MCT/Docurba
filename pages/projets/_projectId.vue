<template>
  <LayoutsCustomApp extended-app-bar private>
    <template #headerPageTitle>
      - {{ project ? project.name : '' }}
    </template>
    <template #headerExtension>
      <v-tabs show-arrows>
        <v-tab
          v-for="tab in tabs"
          :key="tab.text"
          :to="{path: tab.to, query: {region: projectRegion}}"
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
  layout: 'app',
  data () {
    return {
      project: null,
      tabs: [
        { text: 'PAC sec', to: `/projets/${this.$route.params.projectId}/content` },
        { text: 'Jeux de données', to: `/projets/${this.$route.params.projectId}/data` },
        { text: 'Ressources', to: `/projets/${this.$route.params.projectId}/ressources` }
      ]
    }
  },
  computed: {
    projectRegion () {
      return this.project ? this.project.region : ''
    }
  },
  async mounted () {
    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
    this.project = projects ? projects[0] : null
  }
}
</script>
