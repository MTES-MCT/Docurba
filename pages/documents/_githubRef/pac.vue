<template>
  <LayoutsCustomApp>
    <v-container v-if="!loading">
      <v-row>
        <v-col cols="12">
          <h1>
            {{ title }}
          </h1>
          <h2 v-if="collectivite" class="text-subtitle">
            {{ collectivite.intitule }} ({{ collectivite.code }})
          </h2>
        </v-col>
      </v-row>
      <v-row align="center">
        <v-col cols="auto">
          <v-btn :loading="loadingPdf" color="primary" outlined @click="downloadPdf">
            Télécharger en PDF
          </v-btn>
        </v-col>
        <v-spacer />
        <v-col>
          <v-autocomplete
            v-model="searchedSectionPath"
            :loading="opening"
            :items="sections"
            filled
            label="Rechercher une section"
            item-text="name"
            item-value="path"
            hide-details
            @input="opening = true"
          >
            <template #item="data">
              <v-list-item-content>
                <v-list-item-subtitle :style="{ whiteSpace: 'normal' }">
                  {{ data.item.parentPathSubtitle }}
                </v-list-item-subtitle>
                <v-list-item-title>{{ data.item.name }}</v-list-item-title>
              </v-list-item-content>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>
      <v-row>
        <v-col v-for="section in sections" :key="section.url" cols="12">
          <PACSectionCard
            :section="section"
            :git-ref="gitRef"
            :project="project"
            @opened="opening = false"
          />
        </v-col>
      </v-row>
    </v-container>
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>

<script>
import axios from 'axios'
import orderSections from '@/mixins/orderSections.js'

export default {
  mixins: [orderSections],
  layout ({ $user }) {
    if ($user?.profile?.poste === 'ddt' || $user?.profile?.poste === 'dreal') {
      return 'ddt'
    } else {
      return 'default'
    }
  },
  data () {
    return {
      project: {},
      collectivite: null,
      sections: [],
      loadingPdf: false,
      searchedSectionPath: '',
      opening: false,
      gitRef: this.$route.params.githubRef,
      loading: true
    }
  },
  computed: {
    title () {
      if (this.project) {
        return this.project.name
      }

      if (this.gitRef.startsWith('dept')) {
        return 'Trame départementale'
      }
      if (this.gitRef.startsWith('region')) {
        return 'Trame régionale'
      }
      if (this.gitRef === 'main') {
        return 'Trame nationale'
      }

      return null
    }
  },
  async mounted () {
    if (this.gitRef.includes('projet-')) {
      const projectId = this.gitRef.replace('projet-', '')

      const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
      this.project = projects ? projects[0] : {}

      const { data: collectivite } = await axios(`/api/geo/collectivites/${this.project.collectivite_id}`)
      this.collectivite = collectivite
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
    async downloadPdf () {
      this.loadingPdf = true
      await this.$pdf.pdfFromRef(this.gitRef, this.project)
      this.loadingPdf = false
    },
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
