<template>
  <v-row v-if="editedSection && !loading" class="fill-height">
    <!-- This is a hidden feature like the section order waiting to be re implemented -->
    <v-col cols="12">
      <v-text-field
        v-model="editedSection.name"
        :readonly="isReadonly"
        label="Titre dans le sommaire"
        filled
        hide-details
      />
    </v-col>
    <v-col cols="12">
      <PACEditingReadOnlyCard v-show="isReadonly" :section="editedSection" />
    </v-col>
    <v-col cols="12">
      <VTiptap v-model="editedSection.text" :readonly="isReadonly">
        <PACSectionsAttachementsDialog
          :section="section"
        />
      </VTiptap>
    </v-col>
    <v-col cols="12">
      <PACSectionsAttachementsChips :section="section" :attachement-folders="attachementFolders" editable />
    </v-col>
    <v-col cols="12">
      <v-row>
        <v-col v-for="source in selectedDataSources" :key="source.id" cols="6">
          <DataSourceCard :source="source" />
        </v-col>
      </v-row>
    </v-col>
    <v-fab-transition>
      <v-btn
        v-show="modified"
        depressed
        fixed
        bottom
        right
        fab
        color="primary"
        @click="saveSection(editedSection)"
      >
        <v-icon color="white">
          {{ icons.mdiContentSave }}
        </v-icon>
      </v-btn>
    </v-fab-transition>
    <v-dialog v-model="saveDialog" persistent max-width="300px">
      <v-card>
        <v-card-title>
          Sauvegarder ?
        </v-card-title>
        <v-card-text>
          Voulez-vous sauvegarder vos changements ?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn depressed tile color="primary" @click="saveSection(previousSection)">
            Oui
          </v-btn>
          <v-btn depressed tile color="primary" outlined @click="saveDialog = false">
            Non
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
  <VGlobalLoader v-else />
</template>
<script>
import { mdiContentSave } from '@mdi/js'

import axios from 'axios'

export default {
  props: {
    project: {
      type: Object,
      default () { return {} }
    },
    section: {
      type: Object,
      required: true
    },
    readonlyDirs: {
      type: Array,
      default () {
        return []
      }
    },
    gitRef: {
      type: String,
      required: true
    }
  },
  data () {
    const attachementFolders = []

    // if working on a project you need to fetch files from dept and project.
    if (this.section.project_id) {
      attachementFolders.push(this.section.project_id, this.project.towns[0].code_departement)
    } else {
      attachementFolders.push(this.section.dept)
    }

    return {
      icons: { mdiContentSave },
      editedSection: null,
      rawText: '',
      selectedDataSources: [],
      attachementFolders,
      modified: false,
      saveDialog: false
    }
  },
  computed: {
    isReadonly () {
      return !!this.readonlyDirs.find((dir) => {
        return this.editedSection.path.includes(dir) && this.section.slug !== 'new-section'
      })
    }
  },
  watch: {
    async 'section.path' () {
      if (this.modified) {
        this.previousSection = Object.assign({}, this.editedSection)
        this.saveDialog = true
      }

      await this.fetchSection()

      if (this.section.project_id) {
        this.getSectionDataSources()
      }

      this.modified = false
    },
    editedSection: {
      deep: true,
      handler () {
        if (this.section.name !== this.editedSection.name || this.editedSection.text !== this.rawText) {
          this.modified = true
        } else {
          this.modified = false
        }
      }
    }
  },
  mounted () {
    this.fetchSection()

    if (this.project_id) {
      this.getSectionDataSources()
    }
  },
  methods: {
    async fetchSection () {
      this.loading = true

      const path = `/${this.section.path}${this.section.type === 'dir' ? '/intro.md' : ''}`

      const { data: sectionContent } = await axios({
        method: 'get',
        url: '/api/trames/file',
        params: {
          path,
          ref: this.gitRef
        }
      })

      // Replace all metadata with empty string. It should be saved in DB for custom sections.
      const rawText = sectionContent.replace(/---([\s\S]*)---/, '')
      // console.log(rawText)
      const sectionText = this.$md.parse(rawText)

      this.rawText = sectionText
      this.editedSection = Object.assign({ text: sectionText }, this.section)
      this.loading = false
    },
    async getSectionDataSources () {
      const { data: sources } = await this.$supabase.from('sections_data_sources').select('*').match({
        project_id: this.section.project_id,
        section_path: this.section.path
      })

      const sourcesCardsData = await Promise.all(sources.map(async (source) => {
        const { data } = await axios({
          url: source.url,
          meyhod: 'get'
        })

        return Object.assign(data, { sourceId: source.id })
      }))

      this.selectedDataSources = sourcesCardsData
    },
    async updateName () {
      const newName = this.editedSection.name

      await axios({
        method: 'post',
        url: `/api/trames/tree/${this.gitRef}`,
        data: {
          section: this.section,
          newName
        }
      })

      if (this.project.id) {
        const nameIndex = this.section.path.lastIndexOf(this.section.name)
        const newPath = `${this.section.path.substring(0, nameIndex)}${newName}${this.section.type === 'file' ? '.md' : ''}`

        const newPaths = this.project.PAC.map((path) => {
          return path.replace(this.section.path, newPath)
        })

        await this.$supabase.from('projects').update({ PAC: newPaths }).eq('id', this.project.id)
      }
    },
    // section here can be the current section
    // or the previous one in cas of a "are you sure you want to switch section" modal
    async saveSection (section) {
      if (this.section.name !== this.editedSection.name) {
        this.updateName()
      }

      try {
        const filePath = section.type === 'dir' ? `${section.path}/intro${section.path.match(/\//g).length === 1 ? '' : '.md'}` : section.path

        await axios({
          method: 'post',
          url: `/api/trames/${this.gitRef}`,
          data: {
            userId: this.$user.id,
            commit: {
              path: filePath,
              content: btoa(decodeURIComponent(encodeURIComponent(section.text))),
              sha: section.type === 'dir' ? section.introSha : section.sha
            }
          }
        })

        if (this.project.id) {
          this.$notifications.notifyUpdate(this.prooject.id)
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('Error saving data')
      }

      this.modified = false
      this.saveDialog = false
    }
  }
}
</script>
