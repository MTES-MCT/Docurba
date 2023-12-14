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
          :opened-path="$route.query.path"
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
      this.gitRef,
      'main'
    ])

    this.orderSections(sections, supSections)
    this.sections = this.filterPublicsections(sections)

    this.loading = false
  },
  methods: {
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
