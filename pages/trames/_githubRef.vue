<template>
  <LayoutsCustomApp>
    <template v-if="!loading" #headerPageTitle>
      - {{ (project && project.id ? project.name : $route.params.githubRef) | githubRef }}
    </template>
    <!-- <PACEditingTrame
      v-if="!loading"
      :project="project"
      :git-ref="$route.params.githubRef"
    /> -->
    <v-container v-if="!loading">
      <v-row>
        <v-col v-for="section in sections" :key="section.path" cols="12">
          <PACSectionCard :section="section" :git-ref="gitRef" />
        </v-col>
      </v-row>
    </v-container>
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>

<script>
import axios from 'axios'

export default {
  layout: 'app',
  data () {
    return {
      project: {},
      sections: [],
      gitRef: this.$route.params.githubRef,
      loading: true
    }
  },
  async mounted () {
    if (this.gitRef.includes('projet-')) {
      const projectId = this.gitRef.replace('projet-', '')

      const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
      this.project = projects ? projects[0] : {}
    }

    const { data: sections } = await axios({
      method: 'get',
      url: `/api/trames/tree/${this.gitRef}`
    })

    this.sections = sections

    this.loading = false
  }
}
</script>

<style scoped>
.collapse-transition {
  transition: max-width 200ms;
}
</style>
