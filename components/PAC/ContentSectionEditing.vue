<template>
  <v-row class="fill-height">
    <v-col cols="12">
      <v-text-field v-model="editedSection.titre" label="titre" filled hide-details />
    </v-col>
    <v-col cols="12">
      <VTiptap v-model="editedSection.text" :links="PACroots">
        <PACSectionsAttachementsDialog
          :section="section"
          @upload="fetchAttachements"
        />
      </VTiptap>
    </v-col>
    <v-col cols="12">
      <v-chip
        v-for="file in attachements"
        :key="file.name"
        class="mr-1 mb-1"
        color="primary"
        :href="file.url"
      >
        {{ file.name }}
      </v-chip>
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

import pacContent from '@/mixins/pacContent.js'

export default {
  mixins: [pacContent],
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
      },
      attachements: []
    }
  },
  computed: {
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
    },
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
  mounted () {
    this.fetchAttachements()
  },
  methods: {
    getHTML () {
      return this.mdParser.processSync(this.section.text).contents
    },
    saveSection () {
      this.$emit('save', this.editedSection)
      this.modified = false
    },
    // async downloadAttachement (attachement) {
    //   const { data: file, err } = await this.$supabase
    //     .storage
    //     .from('project-annexes')
    //     .download(`/${this.section.dept}${this.section.path}/${attachement.name}`)
    // },
    async fetchAttachements () {
      const folder = this.section.project_id || this.section.dept

      const { data: attachements, err } = await this.$supabase
        .storage
        .from('project-annexes')
        .list(`/${folder}${this.section.path}`, {
          limit: 100,
          offset: 0,
          sortBy: { column: 'name', order: 'asc' }
        })

      if (!err) {
        this.attachements = []

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
