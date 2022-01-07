<template>
  <v-row>
    <v-col cols="12">
      <v-text-field v-model="editedSection.titre" label="titre" filled hide-details />
    </v-col>
    <v-col cols="12">
      <VTiptap v-model="editedSection.text" />
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

export default {
  props: {
    text: {
      type: String,
      default: ''
    },
    titre: {
      type: String,
      default: ''
    }
  },
  data () {
    const mdParser = unified()
      .use(remarkParse)
      .use(remarkRehype, { allowDangerousHtml: true })
      .use(rehypeRaw)
      .use(rehypeSanitize)
      .use(rehypeStringify)

    return {
      mdParser,
      editedSection: {
        text: mdParser.processSync(this.text).contents,
        titre: this.titre
      },
      modified: false,
      icons: {
        mdiContentSave
      }
    }
  },
  watch: {
    text () {
      this.editedSection.text = this.getHTML()
    },
    titre () {
      this.editedSection.titre = this.titre
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
      return this.mdParser.processSync(this.text).contents
    },
    saveSection () {
      this.$emit('save', this.editedSection)
      this.modified = false
    }
  }
}
</script>
