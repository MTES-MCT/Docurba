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
    <!-- <v-container fluid>
      <PACTreeviewContent
        v-if="project"
        :pac-data="project.PAC"
        editable
        @read="savePacItem"
      />
    </v-container> -->
  </LayoutsCustomApp>
</template>

<script>
export default {
  layout: 'app',
  // TODO: Do server side login for this to work.
  // async asyncData ({ route, $supabase }) {
  //   const projectId = route.params.projectId

  //   console.log(projectId)

  //   const { data: projects, error } = await $supabase.from('projects').select('*').eq('id', projectId)

  //   const project = projects ? projects[0] : null

  //   console.log(project, error, projects)

  //   return {
  //     project,
  //     error
  //   }
  // }
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
  },
  methods: {
    async savePacItem (pacItem) {
      const { PAC } = this.project

      const projectPacItem = PAC.find(item => item.path === pacItem.path)
      projectPacItem.checked = pacItem.checked
      // Object.assign(projectPacItem, pacItem)

      await this.$supabase.from('projects').update({ PAC }).eq('id', this.project.id)
    }
  }
}
</script>
