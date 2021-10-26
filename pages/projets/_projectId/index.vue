<template>
  <v-container fluid>
    <PACTreeviewContent v-if="project" :pac-data="project.PAC" />
  </v-container>
</template>

<script>
export default {
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
      project: null
    }
  },
  async mounted () {
    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)

    this.project = projects ? projects[0] : null
  }
}
</script>
