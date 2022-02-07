<template>
  <v-container v-if="loaded" fluid>
    <PACTreeviewContent
      v-if="project"
      :pac-data="project.PAC"
      editable
      @read="savePacItem"
    />
    <v-btn
      fab
      fixed
      bottom
      right
      color="primary"
      @click="downloadPDF"
    >
      <v-icon>{{ icons.mdiDownload }}</v-icon>
    </v-btn>
  </v-container>
  <VGlobalLoader v-else />
</template>
<script>
import { unionBy } from 'lodash'

import unified from 'unified'
import remarkParse from 'remark-parse'
import remarkRehype from 'remark-rehype'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize from 'rehype-sanitize'
import rehypeStringify from 'rehype-stringify'

import jsonCompiler from '@nuxt/content/parsers/markdown/compilers/json.js'

import { mdiDownload } from '@mdi/js'
import { defaultSchema } from '@/assets/sanitizeSchema.js'

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
      loaded: false,
      icons: {
        mdiDownload
      }
    }
  },
  async mounted () {
    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)

    const project = projects ? projects[0] : null

    const { data: deptSections } = await this.$supabase.from('pac_sections_dept').select('*').eq('dept', project.town.code_departement)
    const { data: projectSections } = await this.$supabase.from('pac_sections_project').select('*').eq('project_id', project.id)

    const editedSections = unionBy(projectSections, deptSections, (section) => {
      return section.path
    })

    const mdParser = unified().use(remarkParse)
      .use(remarkRehype, { allowDangerousHtml: true })
      .use(rehypeRaw)
      .use(rehypeSanitize, defaultSchema)
      .use(rehypeStringify)
      .use(jsonCompiler)

    editedSections.forEach((section) => {
      section.body = mdParser.processSync(section.text).result

      const sectionIndex = this.PAC.findIndex(s => s.path === section.path)

      if (sectionIndex >= 0) {
        // The Object Assign here is to keep the order since it's not saved. As could be other properties.
        // Although it might create inconsistenties for versions that get Archived later on.
        this.PAC[sectionIndex] = Object.assign({}, this.PAC[sectionIndex], section)
      } else {
        // console.log('section added', section)
        this.PAC.push(Object.assign({}, section))
      }
    })

    project.PAC = project.PAC.map((section) => {
      return this.enrichSection(section)
    }).filter(s => !!s.body)

    const enrichedProjectSections = projectSections.map((section) => {
      return this.enrichSection(section)
    })

    project.PAC = unionBy(project.PAC, enrichedProjectSections, (section) => {
      return section.path
    })

    this.project = project

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
    },
    enrichSection (section) {
      const enrichedSection = { comments: [] }

      if (typeof (section) === 'object') {
        Object.assign(enrichedSection, section)
      } else {
        const rawSection = this.PAC.find(s => s.path === section)

        // rawSection simply is without comments and read status.
        Object.assign(enrichedSection, rawSection)
      }

      // We set the anchor manually so that it's esier to navigate the content.
      if (enrichedSection.body) {
        const firstChild = enrichedSection.body.children[0]

        if (firstChild) {
          firstChild.props.id = enrichedSection.path.replaceAll(/[^A-Za-z0-9]/g, '__')
        }
      }

      return enrichedSection
    },
    downloadPDF () {
      function closePrint () {
        document.body.removeChild(this.__container__)
      }

      function setPrint () {
        setTimeout(() => {
          this.contentWindow.__container__ = this
          this.contentWindow.onbeforeunload = closePrint
          this.contentWindow.onafterprint = closePrint
          this.contentWindow.focus() // Required for IE
          this.contentWindow.print()
        }, 2000)
      }

      const iframe = document.createElement('iframe')
      iframe.onload = setPrint
      iframe.src = `${window.location.origin}/print/${this.$route.params.projectId}`
      iframe.style.position = 'fixed'
      iframe.style.right = '0'
      iframe.style.bottom = '0'
      iframe.style.width = '0'
      iframe.style.height = '0'
      iframe.style.border = '0'
      document.body.appendChild(iframe)
    }
  }
}
</script>
