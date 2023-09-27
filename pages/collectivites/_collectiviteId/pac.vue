<template>
  <v-container v-if="!loading">
    <v-row align="end">
      <v-col cols="auto">
        <h2>Socle de Porter à connaissance (PAC)</h2>
      </v-col>
      <v-col>
        <DashboardCollectivitesInnerNav :is-epci="isEpci" :collectivite="collectivite" :communes="communes" />
      </v-col>
    </v-row>
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
</template>

<script>
import axios from 'axios'
import orderSections from '@/mixins/orderSections.js'

export default {
  mixins: [orderSections],
  layout: 'app',
  props: {
    isEpci: {
      type: Boolean,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    },
    communes: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      project: {},
      sections: [],
      gitRef: `region-${this.$options.filters.deptToRef(this.collectivite.region.code)}`,
      loading: true
    }
  },
  async mounted () {
    const { data: sections } = await axios({
      method: 'get',
      url: `/api/trames/tree/${this.gitRef}`
    })

    const { data: supSections } = await this.$supabase.from('pac_sections').select('*').in('ref', [
        `projet-${this.project.id}`,
        `dept-${this.project.towns ? this.$options.filters.deptToRef(this.project.towns[0].departementCode) : ''}`,
        `region-${this.project.towns ? this.project.towns[0].regionCode : ''}`,
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
