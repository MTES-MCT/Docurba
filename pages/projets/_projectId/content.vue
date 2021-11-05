<template>
  <v-container fluid>
    <PACTreeviewContent
      v-if="project"
      :pac-data="project.PAC"
      editable
      @read="savePacItem"
    />
  </v-container>
</template>

<script>
export default {
  data () {
    return {
      project: null
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
