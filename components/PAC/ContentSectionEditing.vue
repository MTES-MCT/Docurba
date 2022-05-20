<template>
  <v-row class="fill-height">
    <v-col cols="12">
      <v-text-field v-model="editedSection.titre" label="titre" filled hide-details />
    </v-col>
    <v-col cols="12">
      <VTiptap v-model="editedSection.text" :links="PACroots" :depth="sectionDepth">
        <PACSectionsAttachementsDialog
          :section="section"
          @upload="fetchAttachements"
        />
      </VTiptap>
    </v-col>
    <v-col cols="12">
      <PACSectionsAttachementsChips :files="attachements" />
    </v-col>
    <v-fab-transition>
      <v-btn
        v-show="modified"
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
          <v-btn color="primary" @click="saveSection(previousSection)">
            Oui
          </v-btn>
          <v-btn color="primary" outlined @click="saveDialog = false">
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

import { defaultSchema } from '@/assets/sanitizeSchema.js'

import pacContent from '@/mixins/pacContent.js'

export default {
  mixins: [pacContent],
  props: {
    section: {
      type: Object,
      required: true
    },
    table: {
      type: String,
      required: true
    },
    matchKeys: {
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
      mdParser,
      editedSection: {
        project_id: this.section.project_id,
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
      }, this.matchKeys)

      const { data: savedSection } = await this.$supabase.from(this.table)
        .select('id').match(sectionMatchKeys)

      // const newData = Object.assign({}, this.section, this.editedSection)

      try {
        if (savedSection[0]) {
          await this.$supabase.from(this.table).update(newData).match(sectionMatchKeys)
        } else {
          await this.$supabase.from(this.table).insert([newData])
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
        .list(`/${folder}${this.section.path}`, {
          limit: 100,
          offset: 0,
          sortBy: { column: 'name', order: 'asc' }
        })

      if (!err) {
        for (let i = 0; i < attachements.length; i++) {
          const file = attachements[i]

          const { data } = await this.$supabase
            .storage
            .from('project-annexes')
            .createSignedUrl(`/${folder}${this.section.path}/${file.name}`, 60 * 60)

          file.url = data.signedURL

          this.attachements.push(file)
        }
      }
    }
  }
}
</script>
