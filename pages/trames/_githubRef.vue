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
        <v-col v-for="section in sections" :key="section.url" cols="12">
          <PACSectionCard
            :section="section"
            :git-ref="gitRef"
            :project="project"
            editable
            @edited="toggleEdit"
            @selectionChange="saveSelection"
            @changeOrder="saveOrder"
            @changeTree="updateTreeData"
          />
        </v-col>
      </v-row>
    </v-container>
    <VGlobalLoader v-else />
    <v-dialog v-model="beforeLeaveDialog.visible" width="500">
      <v-card>
        <v-card-title>
          Changements non sauvegardés
        </v-card-title>
        <v-card-text>
          Vous avez des changements non sauvegardés. Etes vous sur de vouloir quitter la page ?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn outlined tile color="primary" @click="beforeLeaveDialog.visible = false">
            Rester
          </v-btn>
          <v-btn tile color="primary" @click="beforeLeaveDialog.next">
            Quitter
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </LayoutsCustomApp>
</template>

<script>
import axios from 'axios'
import orderSections from '@/mixins/orderSections.js'
import departements from '@/assets/data/departements-france.json'

export default {
  mixins: [orderSections],
  beforeRouteLeave (to, from, next) {
    if (this.editedSections.length) {
      this.beforeLeaveDialog.next = next
      this.beforeLeaveDialog.visible = true
    } else { next() }
  },
  layout: 'app',
  data () {
    return {
      project: {},
      sections: [],
      editedSections: [],
      gitRef: this.$route.params.githubRef,
      loading: true,
      beforeLeaveDialog: { visible: false, next: null }
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
    },
    async updateTreeData (section, newName) {
      const sectionPath = section.path // this ref could be modified so it's best to save it here.
      const changedSections = [section]

      // First we need to identify each section that is impacted by a name change.
      function findUpdatedSection (s) {
        changedSections.push(s)

        if (s.children) {
          s.children.forEach(c => findUpdatedSection(c))
        }
      }

      if (section.children) {
        section.children.forEach(c => findUpdatedSection(c))
      }

      const nameIndex = sectionPath.lastIndexOf(section.name)
      // If it's a file, changedSections.length should be 1 and the .md should not impact any other sections.
      const newPath = `${sectionPath.substring(0, nameIndex)}${newName}${section.type === 'file' ? '.md' : ''}`

      // Then we need to edit the path in the table 'PAC_sections' for each impacted section
      await this.$supabase
        .rpc('update_sections_path', {
          payload: changedSections.map((s) => {
            return {
              path: s.path,
              ref: this.gitRef,
              new_path: s.path.replace(sectionPath, newPath)
            }
          })
        })

      // This need to happend after bdd changes because old path will be lost.
      // update the path localy for future saves.
      changedSections.forEach((s) => {
        s.path = s.path.replace(sectionPath, newPath)
      })

      // If it's a project, then selected sections need to be updated with the correct path.
      if (this.project && this.project.id) {
        this.project.PAC = this.project.PAC.map((path) => {
          return path.replace(sectionPath, newPath)
        })

        await this.$supabase.from('projects').update({
          PAC: this.project.PAC
        }).eq('id', this.project.id)
      }

      // Finaly section.name need to be updated.
      section.name = newName
    },
    toggleEdit (sectionPath, val) {
      if (val) {
        this.editedSections.push(sectionPath)
      } else {
        const sectionIndex = this.editedSections.indexOf(sectionPath)
        if (sectionIndex >= 0) {
          this.editedSections.splice(sectionIndex, 1)
        }
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
