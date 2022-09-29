<template>
  <v-row class="fill-height">
    <v-col cols="12">
      <v-text-field v-model="editedSection.titre" :readonly="isReadonly" label="Titre dans le sommaire" filled hide-details />
    </v-col>
    <v-col cols="12">
      <PACEditingReadOnlyCard v-show="isReadonly" :section="editedSection" />
    </v-col>
    <v-col cols="12">
      <VTiptap v-model="editedSection.text" :links="PACroots" :depth="sectionDepth" :readonly="isReadonly">
        <PACSectionsAttachementsDialog
          :section="section"
          @upload="fetchAttachements"
        />
      </VTiptap>
    </v-col>
    <v-col cols="12">
      <PACSectionsAttachementsChips :files="attachements" editable @removed="removeFile" />
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
</template>
<script>
import { mdiContentSave } from '@mdi/js'
import { uniq } from 'lodash'

import unified from 'unified'
import remarkParse from 'remark-parse'
import remarkRehype from 'remark-rehype'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize from 'rehype-sanitize'
import rehypeStringify from 'rehype-stringify'
import pacEditing from '@/mixins/pacEditing.js'

import { defaultSchema } from '@/assets/sanitizeSchema.js'

export default {
  mixins: [pacEditing],
  props: {
    section: {
      type: Object,
      required: true
    },
    attachementsFolders: {
      type: Array,
      default () { return [] }
    }
  },
  data () {
    const mdParser = unified()
      .use(remarkParse)
      .use(remarkRehype, { allowDangerousHtml: true })
      .use(rehypeRaw)
      .use(rehypeSanitize, defaultSchema)
      .use(rehypeStringify)

    return {
      readonlyDirs: [
        '/PAC/Cadre-juridique-et-grands-principes-de-la-planification'
      ],
      mdParser,
      editedSection: {
        dir: this.section.dir,
        path: this.section.path,
        text: mdParser.processSync(this.section.text).contents,
        titre: this.section.titre
      },
      previousSection: {},
      modified: false,
      icons: {
        mdiContentSave
      },
      attachements: [],
      saveDialog: false
    }
  },
  computed: {
    sectionDepth () {
      return this.PAC.find(s => s.path === this.section.path).depth - 2
    },
    PACroots () {
      const roots = this.PAC.filter(section => section.depth === 2).sort((sa, sb) => {
        return sa.ordre - sb.ordre
      })

      return roots
    },
    isReadonly () {
      return !!this.readonlyDirs.find((dir) => {
        return this.editedSection.path.includes(dir)
      })
    }
  },
  watch: {
    'section.path' () {
      this.fetchAttachements()

      if (this.modified) {
        this.previousSection = Object.assign({}, this.editedSection)
        this.saveDialog = true
      }

      this.editedSection = Object.assign({}, this.section, {
        text: this.getHTML()
      })

      this.modified = false
    },
    editedSection: {
      deep: true,
      handler () {
        if (this.section.titre !== this.editedSection.titre || this.editedSection.text !== this.getHTML()) {
          this.modified = true
        } else {
          this.modified = false
        }
      }
    }
  },
  mounted () {
    this.fetchAttachements()
  },
  methods: {
    getHTML () {
      return this.mdParser.processSync(this.section.text).contents
    },
    async saveSection (newData) {
      const sectionMatchKeys = Object.assign({
        path: newData.path
      }, this.tableKeys)

      const { data: savedSection } = await this.$supabase.from(this.table)
        .select('id').match(sectionMatchKeys)

      const savedData = Object.assign({}, newData, this.tableKeys)

      try {
        if (savedSection[0]) {
          await this.$supabase.from(this.table).update(savedData).match(sectionMatchKeys)
        } else {
          await this.$supabase.from(this.table).insert([savedData])
        }

        if (this.tableKeys.project_id) {
          this.$notifications.notifyUpdate(this.tableKeys.project_id)
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('Error saving data')
      }

      this.modified = false
      this.saveDialog = false
    },
    fetchAttachements () {
      this.attachements = []

      const folders = uniq(this.attachementsFolders.concat([
        this.section.project_id || this.section.dept
      ]))

      folders.forEach((folder) => {
        this.fetchFolderFiles(folder)
      })
    },
    async fetchFolderFiles (folder) {
      // const folder = this.section.project_id || this.section.dept

      const { data: attachements, err } = await this.$supabase
        .storage
        .from('project-annexes')
        .list(`${folder}${this.section.path}`, {
          limit: 100,
          offset: 0,
          sortBy: { column: 'name', order: 'asc' }
        })

      if (!err) {
        for (let i = 0; i < attachements.length; i++) {
          const file = attachements[i]
          const filePath = `${folder}${this.section.path}/${file.name}`

          const { data, fileError } = await this.$supabase
            .storage
            .from('project-annexes')
            .createSignedUrl(filePath, 60 * 60)

          if (data && !fileError) {
            // console.log(data)

            file.url = data.signedURL
            file.path = filePath
            file.editable = this.section.project_id ? (folder === this.section.project_id) : true

            this.attachements.push(file)
          } else {
            // console.log('fileError', filePath)
            // console.log(data, fileError)
          }
        }
      }
    },
    removeFile (file) {
      const fileIndex = this.attachements.findIndex(f => f.path === file.path)
      this.attachements.splice(fileIndex, 1)
    }
  }
}
</script>
