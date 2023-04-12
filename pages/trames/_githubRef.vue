<template>
  <LayoutsCustomApp>
    <template v-if="!loading" #headerPageTitle>
      - {{ (project && project.id ? project.name : $route.params.githubRef) | githubRef }}
    </template>
    <!-- <PACEditingTrame
      v-if="!loading"
      :project="project"
      :git-ref="$route.params.githubRef"
    /> -->
    <v-container v-if="!loading">
      <v-row>
        <v-col v-for="section in sections" :key="section.path" cols="12">
          <PACSectionCard
            :section="section"
            :git-ref="gitRef"
            :project="project"
            editable
            @selectionChange="saveSelection"
            @changeOrder="saveOrder"
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
import departements from '@/assets/data/departements-france.json'

export default {
  mixins: [orderSections],
  layout: 'app',
  data () {
    return {
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
        `dept-${this.project.towns ? this.project.towns[0].code_departement : ''}`,
        this.gitRef
    ])

    this.orderSections(sections, supSections)

    function parseSection (section) {
      if (section.children) {
        section.children = section.children.map(section => parseSection(section))
      } else { section.children = [] }

      return Object.assign({
        diff: null
      }, section)
    }

    this.sections = sections.map((section) => {
      return parseSection(section)
    })

    this.loading = false

    this.getDiff()
  },
  methods: {
    async getDiff () {
      let headRef = 'main'

      if (this.project && this.project.id) {
        headRef = `dept-${this.project.towns ? this.project.towns[0].code_departement : ''}`
      }

      if (this.gitRef.includes('dept-')) {
        const dept = this.gitRef.replace('dept-', '')
        // eslint-disable-next-line eqeqeq
        const region = departements.find(d => d.code_departement == dept).code_region
        headRef = `region-${region}`
      }

      // https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#compare-two-commits
      const { data: diffFiles } = await axios({
        url: `/api/trames/compare?basehead=${this.gitRef}...${headRef}`
      })

      this.sections.forEach((section) => {
        this.setDiff(section, diffFiles, headRef)
      })
    },
    setDiff (section, diffFiles, diffRef) {
      const sectionPath = section.type === 'dir' ? `${section.path}/intro.md` : section.path

      const diffFile = diffFiles.find((file) => {
        return file.filename === sectionPath
      })

      const level = diffRef.includes('dept-') ? 'départemental' : 'régionale'

      if (diffFile) {
        section.diff = {
          path: diffFile.filename,
          ref: diffRef,
          label: `Modifications au niveau ${level}`
        }
      }

      if (section.children) {
        section.children.forEach((child) => {
          this.setDiff(child, diffFiles, diffRef)
        })
      }
    },
    async saveSelection (selection) {
      if (selection.selected) {
        this.project.PAC.push(selection.path)
      } else {
        this.project.PAC = this.project.PAC.filter(path => path !== selection.path)
      }

      await this.$supabase.from('projects').update({
        PAC: this.project.PAC
      }).eq('id', this.project.id)
    },
    findParent (section, path) {
      const child = section.children.find(s => s.path === path)

      if (child) {
        return section
      } else {
        return section.children.find((s) => {
          return this.findParent(s, path)
        })
      }
    },
    async saveOrder (sectionPath, orderChange) {
      let parent = this.sections.find(s => s.path === sectionPath)
      let changedSections = null

      if (!parent) {
        this.sections.find((section) => {
          parent = this.findParent(section, sectionPath)
          return parent
        })

        changedSections = parent.children
      } else {
        changedSections = this.sections
      }

      const changedSectionIndex = changedSections.findIndex(s => s.path === sectionPath)
      const newIndex = changedSectionIndex + orderChange

      if (newIndex >= 0 && newIndex < changedSections.length) {
        [
          changedSections[changedSectionIndex],
          changedSections[newIndex]
        ] = [
          changedSections[newIndex],
          changedSections[changedSectionIndex]
        ]

        const updatedSections = changedSections.map((section, index) => {
          section.order = index
          const { path } = section
          return {
            path,
            ref: this.gitRef,
            order: index
          }
        })

        changedSections.sort((s1, s2) => {
          return s1.order - s2.order
        })

        await this.$supabase.from('pac_sections').upsert(updatedSections).select()
      }
    }
  }
}
</script>

<style scoped>
.collapse-transition {
  transition: max-width 200ms;
}
</style>
