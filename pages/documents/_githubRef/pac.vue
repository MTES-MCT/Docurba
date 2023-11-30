<template>
  <LayoutsCustomApp>
    <template v-if="!loading" #headerPageTitle>
      - {{ (project && project.id ? project.name : $route.params.githubRef) | githubRef }}
    </template>
    <v-container v-if="!loading">
      <v-row>
        <v-col v-for="section in sections" :key="section.url" cols="12">
          <PACSectionCard
            :section="section"
            :git-ref="gitRef"
            :project="project"
          />
        </v-col>
      </v-row>
    </v-container>
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>

<script>
import { mdiDownload } from '@mdi/js'
import axios from 'axios'
import orderSections from '@/mixins/orderSections.js'

export default {
  mixins: [orderSections],
  layout: 'app',
  data () {
    return {
      icons: {
        mdiDownload
      },
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

    const { data: supSections } = await this.$supabase.from('pac_sections').select('*').in('ref', [
        `projet-${this.project.id}`,
        `dept-${this.$options.filters.deptToRef(this.project.trame)}`,
        `region-${this.project.region}`,
        'main',
        this.gitRef
    ])

    this.orderSections(sections, supSections)

    if (this.project && this.project.id) {
      this.sections = this.filterSectionsForProject(sections)
    } else {
      this.sections = this.filterPublicsections(sections)
    }

    this.loading = false
  },
  methods: {
    filterSectionsForProject (sections) {
      const paths = this.project.PAC

      const filteredSections = sections.filter(section => paths.includes(section.path))

      return filteredSections.map((section) => {
        return Object.assign({}, section, {
          children: section.children ? this.filterSectionsForProject(section.children) : []
        })
      })
    },
    filterPublicsections (sections) {
      const docType = this.$route.query.document || 'CC'

      const filteredSections = sections.filter((section) => {
        const isAllowed = (!section.path.includes('PAC/Introduction/PAC valid') &&
          !section.path.includes('PP-du-territoire') &&
          !section.path.includes('PAC/Annexes'))

        if (!isAllowed) {
          return false
        } else if (docType === 'PLU') {
          return !section.name.includes('PLUi') && !section.name.includes('carte communale')
        } else if (docType.includes('PLUi')) {
          return !section.name.includes(' PLU ') && !section.name.includes('carte communale')
        } else {
          return !section.name.includes('PLU')
        }
      })

      return filteredSections.map((section) => {
        return Object.assign({}, section, {
          children: section.children ? this.filterPublicsections(section.children) : []
        })
      })
    }
  }
}
</script>
