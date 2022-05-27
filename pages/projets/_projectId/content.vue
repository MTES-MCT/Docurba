<template>
  <v-container v-if="loaded" fluid>
    <PACTreeviewContent
      v-if="project"
      :pac-data="project.PAC"
      editable
      @read="savePacItem"
    />
    <client-only>
      <v-btn
        fab
        fixed
        bottom
        right
        color="primary"
        @click="$print(`/print/${project.id}`)"
      >
        <v-icon>{{ icons.mdiDownload }}</v-icon>
      </v-btn>
    </client-only>
  </v-container>
  <VGlobalLoader v-else />
</template>
<script>
// import { unionBy, omitBy, isNil } from 'lodash'

import unified from 'unified'
import remarkParse from 'remark-parse'
import remarkRehype from 'remark-rehype'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize from 'rehype-sanitize'
import rehypeStringify from 'rehype-stringify'

import jsonCompiler from '@nuxt/content/parsers/markdown/compilers/json.js'

import { mdiDownload } from '@mdi/js'
import { defaultSchema } from '@/assets/sanitizeSchema.js'

import unifiedPAC from '@/mixins/unifiedPac.js'

export default {
  mixins: [unifiedPAC],
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
    const mdParser = unified().use(remarkParse)
      .use(remarkRehype, { allowDangerousHtml: true })
      .use(rehypeRaw)
      .use(rehypeSanitize, defaultSchema)
      .use(rehypeStringify)
      .use(jsonCompiler)

    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
    const project = projects ? projects[0] : null

    const { data: deptSections } = await this.$supabase.from('pac_sections_dept').select('*').eq('dept', project.towns[0].code_departement)
    const { data: projectSections } = await this.$supabase.from('pac_sections_project').select('*').eq('project_id', project.id)

    // TODO: Need to add the reading and unify of comments and checked markers here.
    project.PAC = this.unifyPacs([projectSections, deptSections, this.PAC], project.PAC.map((s) => {
      return s.path || s
    }))

    project.PAC.forEach((section) => {
      // Parse the body only if text was edited.
      if (section.text) { section.body = mdParser.processSync(section.text).result }
    })

    // The next two enrich and the union should be refactored because there is some useless steps here.
    project.PAC = project.PAC.map((section) => {
      return this.enrichSection(section)
    }).filter(s => !!s.body)

    this.project = project

    this.loaded = true
  },
  methods: {
    _project () {
      return this.project
    },
    savePacItem (pacItem) {
      // TODO: This need to be changed into its own table.

      const { PAC } = this.project

      const projectPacItem = PAC.find(item => item.path === pacItem.path)
      projectPacItem.checked = pacItem.checked
      // Object.assign(projectPacItem, pacItem)

      // console.log(pacItem, projectPacItem)

      // await this.$supabase.from('projects').update({ PAC }).eq('id', this.project.id)
    },
    enrichSection (section) {
      const enrichedSection = Object.assign({ comments: [] }, section)
      // const rawSection = this.PAC.find(s => s.path === section)

      // We set the anchor manually so that it's esier to navigate the content.
      if (enrichedSection.body) {
        const firstChild = enrichedSection.body.children[0]

        if (firstChild) {
          firstChild.props.id = enrichedSection.path.replaceAll(/[^A-Za-z0-9]/g, '__')
        }
      }

      return enrichedSection
    }
  }
}
</script>
