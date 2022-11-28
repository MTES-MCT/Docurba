<template>
  <LayoutsCustomApp>
    <template #headerPageTitle>
      - {{ project ? project.name : '' }}
    </template>
    <PACEditingTrame
      v-if="!loading"
      :pac-data="PAC"
      table="pac_sections_project"
      :table-keys="{
        project_id: project.id
      }"
      :sections-list="project.PAC"
      :project="project"
    />
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>

<script>
import unified from 'unified'
import remarkParse from 'remark-parse'

import unifiedPAC from '@/mixins/unifiedPac.js'

export default {
  mixins: [unifiedPAC],
  layout: 'app',
  async asyncData ({ $content }) {
    const PAC = await $content('PAC', {
      deep: true,
      text: true
    }).fetch()

    const originalPAC = PAC.map((section) => {
      return Object.assign({}, section)
    })

    return {
      PAC,
      originalPAC
    }
  },
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
    const mdParser = unified().use(remarkParse)
    this.mdParser = mdParser

    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
    this.project = projects ? projects[0] : null

    // Subscribe to project changes for easy flux update
    this.subscribeToBdd(projectId)
    window.addEventListener('focus', () => {
      this.subscribeToBdd(projectId)
    })

    // Get the data from DB for each level of PAC for this project.
    const [regionSections, deptSections, projectSections] = await Promise.all([
      this.fetchSections('pac_sections_region', {
        region: this.project.towns[0].code_region
      }),
      this.fetchSections('pac_sections_dept', {
        dept: this.project.towns[0].code_departement
      }),
      this.fetchSections('pac_sections_project', {
        project_id: this.project.id
      })
    ])

    // Merge data of multiple PACs using unifiedPac.js mixin.
    this.PAC = this.unifyPacs([
      projectSections,
      deptSections,
      regionSections,
      this.PAC
    ])

    // TODO: This is duplicated in all section read
    this.PAC.forEach((section) => {
      if (section.text) {
        section.body = mdParser.parse(section.text)
      }
    })

    this.loading = false
  },
  beforeDestroy () {
    if (this.projectSectionsSub) {
      this.$supabase.removeChannel(this.projectSectionsSub)
    }
  },
  methods: {
    async subscribeToBdd (projectId) {
      if (this.projectSectionsSub) {
        await this.$supabase.removeChannel(this.projectSectionsSub)
      }

      this.projectSectionsSub = this.$supabase.channel('public:pac_sections_project')
        .on('postgres_changes', { event: '*', schema: 'public', table: 'pac_sections_project', filter: `project_id=eq.${projectId}` }, (update) => {
          this.spliceSection(this.PAC, update)
        }).subscribe()
    }
  }
}
</script>

<style scoped>
.collapse-transition {
  transition: max-width 200ms;
}
</style>
