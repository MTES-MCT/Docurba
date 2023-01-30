<template>
  <v-row v-if="editedSection && !loading" class="fill-height">
    <v-col cols="12">
      <v-text-field v-model="editedSection.titre" :readonly="isReadonly" label="Titre dans le sommaire" filled hide-details />
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
      <PACSectionsAttachementsChips :attachement-folders="attachementFolders" editable />
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
    contentRef: {
      type: String,
      required: true
    },
    readonlyDirs: {
      type: Array,
      default () {
        return []
      }
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
      selectedDataSources: [],
      attachementFolders
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
      await this.fetchSection()
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

      // console.log(this.section, `/${this.section.path}/${this.section.type === 'dir' ? 'intro.md' : '.md'}`)

      const { data: sectionContent } = await axios({
        method: 'get',
        url: '/api/trames/file',
        params: {
          path: `/${this.section.path}/${this.section.type === 'dir' ? 'intro.md' : '.md'}`,
          ref: this.contentRef
        }
      })

      // Replace all metadata with empty string. It should be saved in DB for custom sections.
      const rawText = sectionContent.replace(/---([\s\S]*)---/, '')
      const sectionText = this.$md.parse(decodeURIComponent(rawText))

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
    }
  }
}
</script>
