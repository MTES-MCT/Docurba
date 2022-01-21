<template>
  <v-row class="fill-height">
    <v-col cols="12">
      <v-text-field v-model="editedSection.titre" label="titre" filled hide-details />
    </v-col>
    <v-col cols="12">
      <VTiptap v-model="editedSection.text">
        <v-dialog width="800px">
          <template #activator="{on}">
            <v-btn icon v-on="on">
              <v-icon>{{ icons.mdiPaperclip }}</v-icon>
            </v-btn>
          </template>
          <v-card>
            <v-card-title>
              Ajouter une annexe
            </v-card-title>
            <v-tabs v-model="ressourcesTab" grow>
              <v-tab>
                Fichiers
              </v-tab>
              <v-tab>
                Data
              </v-tab>
            </v-tabs>
            <v-tabs-items v-model="ressourcesTab">
              <v-tab-item>
                <v-card-text>
                  Fichiers
                </v-card-text>
              </v-tab-item>
              <v-tab-item>
                <v-card-text>
                  Data
                </v-card-text>
              </v-tab-item>
            </v-tabs-items>
          </v-card>
        </v-dialog>
      </VTiptap>
    </v-col>
    <v-fab-transition>
      <v-btn
        v-show="modified"
        fixed
        bottom
        right
        fab
        color="primary"
        @click="saveSection"
      >
        <v-icon color="white">
          {{ icons.mdiContentSave }}
        </v-icon>
      </v-btn>
    </v-fab-transition>
  </v-row>
</template>
<script>
import { mdiContentSave, mdiPaperclip } from '@mdi/js'

import unified from 'unified'
import remarkParse from 'remark-parse'
import remarkRehype from 'remark-rehype'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize from 'rehype-sanitize'
import rehypeStringify from 'rehype-stringify'

import { defaultSchema } from '@/assets/sanitizeSchema.js'

export default {
  props: {
    section: {
      type: Object,
      required: true
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
        text: mdParser.processSync(this.section.text).contents,
        titre: this.section.titre
      },
      modified: false,
      icons: {
        mdiContentSave,
        mdiPaperclip
      },
      ressourcesTab: 0
    }
  },
  watch: {
    'section.text' () {
      this.editedSection.text = this.getHTML()
    },
    'section.titre' () {
      this.editedSection.titre = this.section.titre
    },
    editedSection: {
      deep: true,
      handler () {
        if (this.titre !== this.editedSection.titre || this.editedSection.text !== this.getHTML()) {
          this.modified = true
        } else {
          this.modified = false
        }
      }
    }
  },
  methods: {
    getHTML () {
      return this.mdParser.processSync(this.section.text).contents
    },
    saveSection () {
      this.$emit('save', this.editedSection)
      this.modified = false
    }
  }
}
</script>
