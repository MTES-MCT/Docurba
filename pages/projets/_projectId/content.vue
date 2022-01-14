<template>
  <v-container v-if="loaded" fluid>
    <PACTreeviewContent
      v-if="project"
      :pac-data="project.PAC"
      editable
      @read="savePacItem"
    />
  </v-container>
  <VGlobalLoader v-else />
</template>
<script>
import unified from 'unified'
import remarkParse from 'remark-parse'

export default {
  provide () {
    return {
      pacProject: this._project
    }
  },
  async asyncData ({ $content }) {
    const PAC = await $content('PAC', {
      deep: true,
      text: true
    }).fetch()

    return {
      PAC
    }
  },
  data () {
    return {
      project: null,
      loaded: false
    }
  },
  async mounted () {
    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)

    this.project = projects ? projects[0] : null

    const { data: deptSections } = await this.$supabase.from('pac_sections_dept').select('*').eq('dept', this.project.town.code_departement)

    const mdParser = unified().use(remarkParse)
    this.mdParser = mdParser

    deptSections.forEach((section) => {
      section.body = mdParser.parse(section.text)
      const sectionIndex = this.PAC.findIndex(s => s.path === section.path)

      if (sectionIndex >= 0) {
        // The Object Assign here is to keep the order since it's not saved. As could be other properties.
        // Although it might create inconsistenties for versions that get Archived later on.
        this.PAC[sectionIndex] = Object.assign({}, this.PAC[sectionIndex], section)
      } else {
        this.PAC.push(Object.assign({}, section))
      }
    })

    this.project.PAC = this.project.PAC.map((section) => {
      if (typeof (section) === 'object') {
        return Object.assign({
          comments: []
        }, section)
      } else {
        const rawSection = this.PAC.find(s => s.path === section)
        return Object.assign({
          comments: []
        }, rawSection)
      }
    })

    console.log(this.project.PAC)
    this.loaded = true
  },
  methods: {
    _project () {
      return this.project
    },
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
