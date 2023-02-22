<template>
  <LayoutsCustomApp>
    <template #headerPageTitle>
      - {{ project ? project.name : '' }}
    </template>
    <PACEditingTrame
      v-if="!loading"
      :project="project"
      :git-ref="`projet-${project.id}`"
    />
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>

<script>
// import unified from 'unified'
// import remarkParse from 'remark-parse'

// import unifiedPAC from '@/mixins/unifiedPac.js'

export default {
  // mixins: [unifiedPAC],
  layout: 'app',
  // async asyncData ({ $content }) {
  //   const PAC = await $content('PAC', {
  //     deep: true,
  //     text: true
  //   }).fetch()

  //   const originalPAC = PAC.map((section) => {
  //     return Object.assign({}, section)
  //   })

  //   return {
  //     PAC,
  //     originalPAC
  //   }
  // },
  data () {
    return {
      project: null,
      loading: true,
      collapsedTree: false,
      selectedSection: null,
      projectSectionsSub: null
    }
  },
  async mounted () {
    // const mdParser = unified().use(remarkParse)
    // this.mdParser = mdParser

    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
    this.project = projects ? projects[0] : null

    // Subscribe to project changes for easy flux update
    // this.subscribeToBdd(projectId)
    // window.addEventListener('focus', () => {
    //   this.subscribeToBdd(projectId)
    // })

    this.loading = false
  },
  // beforeDestroy () {
  //   if (this.projectSectionsSub) {
  //     this.$supabase.removeChannel(this.projectSectionsSub)
  //   }
  // },
  methods: {
    // async subscribeToBdd (projectId) {
    //   if (this.projectSectionsSub) {
    //     await this.$supabase.removeChannel(this.projectSectionsSub)
    //   }

    //   this.projectSectionsSub = this.$supabase.channel(`public:pac_sections_project:project_id=eq.${projectId}`)
    //     .on('postgres_changes', { event: '*', schema: 'public', table: 'pac_sections_project', filter: `project_id=eq.${projectId}` }, (update) => {
    //       this.spliceSection(this.PAC, update)
    //     }).subscribe()
    // }
  }
}
</script>

<style scoped>
.collapse-transition {
  transition: max-width 200ms;
}
</style>
