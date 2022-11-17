<template>
  <v-container v-if="loaded">
    <iframe v-if="pdfUrl" :src="pdfUrl" style="width: 100%;height: calc(100vh - 200px);border: none;" />
    <PACTreeviewContent
      v-if="project && !pdfUrl"
      :pac-data="project.PAC"
      editable
      @read="savePacItem"
    />
    <client-only>
      <v-btn
        v-if="!pdfUrl"
        depressed
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
import { mdiDownload } from '@mdi/js'

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
      pdfUrl: null,
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

    this.project = project

    if (this.project.trame) {
      await this.setPACFromTrame()
    } else {
      await this.loadPACFile()
    }

    // Start Analytics
    this.$matomo([
      'trackEvent', 'Projet PAC', 'Content',
          `${this.project.doc_type} - ${this.project.epci ? this.project.epci.label : this.project.towns[0].nom_commune}`
    ])
    // End Analytics

    this.loaded = true
  },
  methods: {
    _project () {
      return this.project
    },
    async setPACFromTrame () {
      const PAC = await this.$content('PAC', {
        deep: true,
        text: true
      }).fetch()

      this.PAC = PAC

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

      // TODO: Need to add the reading and unify of comments and checked markers here.
      this.project.PAC = this.unifyPacs([
        projectSections,
        deptSections,
        regionSections,
        this.PAC
      ], this.project.PAC.map((s) => {
        return s.path || s
      }))

      // TODO: // This is duplicated in all read sections
      this.project.PAC.forEach((section) => {
      // Parse the body only if text was edited.
        if (section.text) { section.body = this.$mdParse(section.text) }
      })

      // The next two enrich and the union should be refactored because there is some useless steps here.
      this.project.PAC = this.project.PAC.map((section) => {
        return this.enrichSection(section)
      }).filter(s => !!s.body)
    },
    async loadPACFile () {
      const { signedURL: pdfUrl, err } = await this.$supabase.storage
        .from('projects-pac')
        .createSignedUrl(`${this.project.id}/pac.pdf`, 60 * 60)

      if (!err) {
        this.pdfUrl = pdfUrl
      } else {
        // eslint-disable-next-line no-console
        console.log('err loading pdf', err)
      }
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
