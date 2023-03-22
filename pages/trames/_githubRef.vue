<template>
  <LayoutsCustomApp>
    <template v-if="!loading" #headerPageTitle>
      - {{ (project && project.id ? project.name : $route.params.githubRef) | githubRef }}
    </template>
    <PACEditingTrame
      v-if="!loading"
      :project="project"
      :git-ref="$route.params.githubRef"
    />
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>

<script>

export default {
  layout: 'app',
  data () {
    return {
      project: {},
      loading: true
    }
  },
  async mounted () {
    const githubRef = this.$route.params.githubRef

    if (githubRef.includes('projet-')) {
      const projectId = githubRef.replace('projet-', '')

      const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
      this.project = projects ? projects[0] : {}
    }

    this.loading = false
  }
}
</script>

<style scoped>
.collapse-transition {
  transition: max-width 200ms;
}
</style>
