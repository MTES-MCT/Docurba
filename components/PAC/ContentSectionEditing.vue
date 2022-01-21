<template>
  <v-row class="fill-height">
    <v-col cols="12">
      <v-text-field v-model="editedSection.titre" label="titre" filled hide-details />
    </v-col>
    <v-col cols="12">
      <VTiptap v-model="editedSection.text">
        <PACSectionsAttachementsDialog :section="section" />
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
import { mdiContentSave } from '@mdi/js'

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
        mdiContentSave
      }
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
