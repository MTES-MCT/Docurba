<template>
  <v-container v-if="!loading">
    <v-row>
      <v-col cols="12">
        <PACEditingAdvicesCard :avoided-tags="(project && project.id) ? [] : ['projet']" />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-text-field
          v-if="project && renameMode"
          v-model="newName"
          autofocus
          hide-details
          class="rename-field"
          @keydown.enter="renameProject"
        >
          <template #append-outer>
            <v-btn icon color="primary" @click="renameProject">
              <v-icon>{{ icons.mdiCheck }}</v-icon>
            </v-btn>
            <v-btn icon @click="toggleRenameMode(false)">
              <v-icon>{{ icons.mdiClose }}</v-icon>
            </v-btn>
          </template>
        </v-text-field>
        <h1 v-else>
          {{ title }}
        </h1>
        <h2 v-if="collectivite" class="text-subtitle">
          {{ collectivite.intitule }} ({{ collectivite.code }})
        </h2>

        <div class="mt-4">
          <v-btn color="primary" depressed :disabled="editingSections.length > 0" @click="editable = !editable">
            {{ editable ? 'Prévisualiser' : 'Éditer' }}
          </v-btn>
          <v-btn v-if="project" color="primary" outlined class="ml-2" @click="shareDialog = true">
            Partager
          </v-btn>
          <v-menu offset-y left>
            <template #activator="{ attrs, on }">
              <v-btn
                :loading="loadingPdf"
                class="ml-2"
                color="primary"
                :style="{ borderRadius: '4px' }"
                icon
                outlined
                v-bind="attrs"
                v-on="on"
              >
                <v-icon>{{ icons.mdiDotsVertical }}</v-icon>
              </v-btn>
            </template>

            <v-list>
              <v-list-item @click="downloadPdf">
                <v-list-item-title>Télécharger en PDF</v-list-item-title>
              </v-list-item>
              <v-list-item v-if="project" @click="toggleRenameMode(true)">
                <v-list-item-title>Renommer le PAC</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
      </v-col>
      <v-col>
        <v-autocomplete
          v-model="searchedSectionPath"
          :loading="opening"
          :items="autocompleteSectionItems"
          filled
          label="Rechercher une section"
          item-text="name"
          item-value="path"
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
      <v-col v-for="section in filteredSections" :key="section.url" cols="12">
        <PACSectionCard
          :section="section"
          :git-ref="gitRef"
          :project="project || {}"
          :opened-path="searchedSectionPath"
          :editable="editable"
          @editing="handleEditing"
          @selectionChange="saveSelection"
          @changeOrder="saveOrder"
          @changeTree="updateTreeData"
          @opened="opening = false"
        />
      </v-col>
    </v-row>

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

    <DashboardSharePACDialog v-if="project" v-model="shareDialog" :project="project" />
  </v-container>
  <v-container v-else class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12">
        <VGlobalLoader />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'
import { groupBy } from 'lodash'
import { mdiDotsVertical, mdiCheck, mdiClose } from '@mdi/js'
import orderSections from '@/mixins/orderSections.js'

export default {
  mixins: [orderSections],
  beforeRouteLeave (to, from, next) {
    if (this.editingSections.length) {
      this.beforeLeaveDialog.next = next
      this.beforeLeaveDialog.visible = true
    } else { next() }
  },
  layout: 'ddt',
  data () {
    return {
      icons: {
        mdiDotsVertical, mdiCheck, mdiClose
      },
      project: null,
      sections: [],
      editingSections: [],
      gitRef: this.$route.params.githubRef,
      loading: true,
      beforeLeaveDialog: { visible: false, next: null },
      collectivite: null,
      editable: false,
      opening: false,
      searchedSectionPath: null,
      shareDialog: false,
      loadingPdf: false,
      renameMode: false,
      newName: ''
    }
  },
  computed: {
    headRef () {
      return this.$options.filters.headRef(this.gitRef, this.project)
    },
    autocompleteSectionItems () {
      const flatSections = this.getFlatSections(this.sections)
      return flatSections.map(s => ({
        name: s.name,
        path: s.path,
        parentPathSubtitle: s.path.substr(0, s.path.lastIndexOf('/')).replace('PAC/', '').replaceAll('/', ' / ')
      }))
    },
    filteredSections () {
      const paths = this.project?.PAC

      function filterSelectedSections (sections) {
        const filtered = sections.filter(section => paths.includes(section.path))

        return filtered.map((section) => {
          return Object.assign({}, section, {
            children: section.children ? filterSelectedSections(section.children) : []
          })
        })
      }

      if (this.project && paths && !this.editable) {
        return filterSelectedSections(this.sections)
      }

      return this.sections
    },
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
      this.project = projects ? projects[0] : null

      const { data: collectivite } = await axios(`/api/geo/collectivites/${this.project.collectivite_id}`)
      this.collectivite = collectivite
    }

    const { data: sections } = await axios({
      method: 'get',
      url: `/api/trames/tree/${this.gitRef}`,
      params: {
        ghostRef: this.headRef
      }
    })

    let { data: supSections } = await this.$supabase
      .from('pac_sections')
      .select('*')
      .in('ref', this.$options.filters.allHeadRefs(this.gitRef, this.project))

    const { data: histories } = await axios.get(`/api/trames/tree/${this.gitRef}/history`, {
      params: {
        paths: sections
          .filter(s => !s.ghost)
          .map(s => s.type === 'file' ? s.path : (s.path + '/intro.md'))
      }
    })

    // This code should prevent using multiple value when parsing.
    const groupedSupSections = groupBy(supSections, s => s.path)
    supSections = Object.keys(groupedSupSections).map((path) => {
      return groupedSupSections[path].find(s => s.ref.includes('projet')) ||
          groupedSupSections[path].find(s => s.ref.includes('dept')) ||
          groupedSupSections[path].find(s => s.ref.includes('test')) ||
          groupedSupSections[path].find(s => s.ref.includes('region')) ||
          groupedSupSections[path].find(s => s.ref.includes('main'))
    })

    this.orderSections(sections, supSections)

    function parseSection (section, supSections, parent) {
      const groupedChildren = groupBy(section.children, c => c.name)
      const groupedKeys = Object.keys(groupedChildren)

      groupedKeys.forEach((key) => {
        const group = groupedChildren[key]

        if (group.length > 1) {
          group.forEach((section) => {
            section.isDuplicated = true
          })
        }
      })

      if (section.children) {
        section.children = section.children.map(s => parseSection(s, supSections, section))
      } else { section.children = [] }

      const supSection = supSections.find((supSection) => {
        return section.path === supSection.path
      })

      return Object.assign({
        id: supSection?.id,
        diff: null,
        diffCount: 0,
        parentSha: supSection ? supSection.parent_sha : ''
      }, section)
    }

    this.sections = sections.map((section) => {
      const s = parseSection(section, supSections)
      s.editDate = histories.find(h => h.path.replace('/intro.md', '') === s.path)?.commit?.date
      return s
    })

    this.loading = false

    this.getDiff(supSections)
  },
  methods: {
    getFlatSections (sections) {
      return sections.flatMap(s => [s, ...this.getFlatSections(s.children)])
    },
    async getDiff (supSections) {
      // https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#compare-two-commits
      const { data } = await axios({
        url: `/api/trames/compare?basehead=${this.gitRef}...${this.headRef}`
      })

      const diffFiles = data.files.filter((file) => {
        const section = supSections.find((s) => {
          return file.filename.replace('/intro.md', '') === s.path
        })

        return file.changes > 0 && (!section || section.parent_sha !== file.sha)
      })

      this.sections.forEach((section) => {
        this.setDiff(section, diffFiles, this.headRef)
      })
    },
    setDiff (section, diffFiles, diffRef) {
      const sectionPath = section.type === 'dir' ? `${section.path}/intro.md` : section.path

      const diffFile = diffFiles.find((file) => {
        return file.filename === sectionPath && file.changes > 0
      })

      if (diffFile) {
        const level = diffRef.includes('dept-') ? 'départemental' : (diffRef.includes('region-') ? 'régional' : 'national')

        section.diff = {
          path: diffFile.filename,
          ref: diffRef,
          sha: diffFile.sha,
          label: `Modifications au niveau ${level}`
        }
      }

      if (section.children && section.children.length) {
        section.diffCount = section.children.reduce((diffCount, child) => {
          return diffCount + this.setDiff(child, diffFiles, diffRef)
        }, 0)

        return section.diffCount + (diffFile ? 1 : 0)
      } else {
        return diffFile ? 1 : 0
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
    findSection (sections, path) {
      const flatSections = this.getFlatSections(sections)
      const section = flatSections.find(s => s.path === path)

      if (!section) {
        throw new Error('Section not found')
      }

      return section
    },
    async saveOrder (section, orderChange) {
      const sectionPath = section.path
      const parentPath = section.path.substring(0, section.path.lastIndexOf('/'))

      const sections = this.sections.includes(section)
        ? this.sections
        : this.findSection(this.sections, parentPath).children

      const changedSections = sections.filter(s => !s.ghost)
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

        sections.sort((a, b) => {
          if (a.ghost && !b.ghost) {
            return 1
          } else if (!a.ghost && b.ghost) {
            return -1
          } else {
            return a.order - b.order
          }
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
    handleEditing (sectionPath, editing) {
      if (editing) {
        this.editingSections.push(sectionPath)
      } else {
        const sectionIndex = this.editingSections.indexOf(sectionPath)
        if (sectionIndex >= 0) {
          this.editingSections.splice(sectionIndex, 1)
        }
      }
    },
    async downloadPdf () {
      this.loadingPdf = true
      await this.$pdf.pdfFromRef(this.gitRef, this.project)
      this.loadingPdf = false
    },
    toggleRenameMode (enable) {
      this.newName = this.project.name
      this.renameMode = enable
    },
    async renameProject () {
      if (!this.newName.trim().length) {
        return
      }

      await this.$supabase.from('projects').update({ name: this.newName }).eq('id', this.project.id)
      this.project.name = this.newName
      this.renameMode = false
    }
  }
}
</script>

<style scoped>
.collapse-transition {
  transition: max-width 200ms;
}
</style>

<style>
.v-autocomplete__content {
  width: 0; /* will use min-width, so the autocomplete list will be the same width as the input */
}

.rename-field {
  padding: 0;
  margin: 0;
  max-width: 24rem;
}

.rename-field input {
  font-size: 32px;
  font-weight: 700;
  line-height: 48px;
  max-height: 48px;
}
</style>
