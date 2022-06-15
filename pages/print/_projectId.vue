<template>
  <div>
    <v-app-bar
      elevation="0"
      color="white"
      class="fr-header"
      height="68px"
      absolute
    >
      <div class="fr-header__body">
        <div class="fr-container">
          <div class="fr-header__body-row">
            <div class="fr-header__brand fr-enlarge-link">
              <div class="fr-header__brand-top">
                <div class="fr-header__logo">
                  <a href="/" title="Accueil - Docurba">
                    <p class="fr-logo">
                      république
                      <br>française
                    </p>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <v-spacer />
      <div v-if="project" class="ddt-text text-right">
        Direction départementale des territoires <br>
        {{ project.towns[0].nom_departement }}
      </div>
    </v-app-bar>
    <table>
      <thead>
        <tr>
          <td>
            <div class="header-space" />
          </td>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <PACPDFGardeTemplate v-if="project" :project="project" />
          </td>
        </tr>
        <tr>
          <td>
            <PACPDFTableOfContent v-if="project" :project="project" />
          </td>
        </tr>
      </tbody>
    </table>
    <table>
      <tbody>
        <tr>
          <td>
            <PACPDFPagesTemplate v-if="project" :pac-data="project.PAC" />
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <td>
            <div class="footer-space" />
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<script>
import { unionBy, omitBy, isNil } from 'lodash'

import unified from 'unified'
import remarkParse from 'remark-parse'
import remarkRehype from 'remark-rehype'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize from 'rehype-sanitize'
import rehypeStringify from 'rehype-stringify'

import jsonCompiler from '@nuxt/content/parsers/markdown/compilers/json.js'

import { defaultSchema } from '@/assets/sanitizeSchema.js'

export default {
  layout: 'print',
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
      PACroots: []
    }
  },
  head () {
    return {
      title: this.project ? this.project.name : 'PAC',
      titleTemplate: ''
    }
  },
  async mounted () {
    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)

    const project = projects ? projects[0] : null

    const { data: deptSections } = await this.$supabase.from('pac_sections_dept').select('*').eq('dept', project.towns[0].code_departement)
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
      if (section.text) { section.body = mdParser.processSync(section.text).result }

      const sectionIndex = this.PAC.findIndex(s => s.path === section.path)

      if (sectionIndex >= 0) {
        // The Object Assign here is to keep the order since it's not saved. As could be other properties.
        // Although it might create inconsistenties for versions that get Archived later on.
        this.PAC[sectionIndex] = Object.assign({}, this.PAC[sectionIndex], omitBy(section, isNil))
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

    project.PAC = unionBy(enrichedProjectSections, project.PAC, (section) => {
      return section.path
    })

    this.project = project
  },
  methods: {
    enrichSection (section) {
      const enrichedSection = { comments: [] }
      const rawSection = this.PAC.find(s => s.path === section)

      if (typeof (section) === 'object') {
        Object.assign(enrichedSection, section, omitBy(rawSection, isNil))
      } else {
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
    }
  }
}
</script>

<style scoped>
  table {
    max-width: 100%;
    width: 100%;
    table-layout: fixed;
  }

  table, tr, td {
    page-break-inside: avoid;
  }

  .ddt-text {
    font-size: 14pt;
    font-weight: 700;
  }

 .header-space {
   height: calc(68px + 8.5mm);
 }

 .footer-space {
   /* height: calc(68px + 8.5mm); */
   height: 8.5mm;
 }

.fr-header .fr-header__body-row, .fr-header .fr-header__logo, .fr-header .fr-logo {
  padding: 0mm !important;
  margin: 0mm !important
}

.fr-header a {
  color: #1e1e1e;
  text-decoration: none;
}
</style>
