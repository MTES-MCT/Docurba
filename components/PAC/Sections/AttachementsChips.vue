<template>
  <v-row>
    <v-col cols="12">
      <v-chip
        v-for="file in files"
        :key="file.id"
        class="mr-1 mb-1"
        color="primary"
        :href="file.link"
        target="_blank"
        :small="small"
        :close="editable && file.path.includes(gitRef)"
        @click:close="openDialog(file)"
      >
        {{ file.name }}
      </v-chip>
    </v-col>
    <v-dialog max-width="600px" :value="dialog">
      <v-card>
        <v-card-title>
          Supprimer {{ selectedFile.name }} ?
        </v-card-title>

        <v-card-actions>
          <v-spacer />
          <v-btn depressed tile text color="primary" @click="dialog = false">
            Annuler
          </v-btn>
          <v-btn depressed tile color="primary" @click="removeFile(selectedFile)">
            Supprimer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>

export default {
  props: {
    section: {
      type: Object,
      required: true
    },
    small: {
      type: Boolean,
      default: false
    },
    editable: {
      type: Boolean,
      default: false
    },
    gitRef: {
      type: String,
      required: true
    },
    project: {
      type: Object,
      default () { return {} }
    }
  },
  data () {
    return {
      files: [],
      dialog: false,
      selectedFile: {},
      subscription: null
    }
  },
  // watch: {
  //   'section.path' () {
  //     this.fetchAttachements()
  //   }
  // },
  mounted () {
    this.fetchAttachements()

    if (this.editable) {
      this.subscription = this.$supabase
        .channel(`public:pac_sections:ref=eq.${this.gitRef}`)
        .on('postgres_changes', {
          event: '*',
          schema: 'public',
          table: 'pac_sections',
          filter: `ref=eq.${this.gitRef}`
        }, (payload) => {
          if (payload.new.path === this.section.path) {
            this.fetchAttachements()
          }
        }).subscribe()
    }
  },
  beforeDestroy () {
    this.$supabase.removeChannel(this.subscription)
  },
  methods: {
    openDialog (file) {
      this.dialog = true
      this.selectedFile = file
    },
    async fetchAttachements () {
      const { data: sectionsData } = await this.$supabase.from('pac_sections').select('attachements, ref').match({
        path: this.section.path
      }).in('ref', [
        `projet-${this.project.id}`,
        `dept-${this.$options.filters.deptToRef(this.project.trame)}`,
        this.gitRef
      ])

      const files = []

      sectionsData.forEach(({ ref, attachements }) => {
        attachements.forEach((attachement) => {
          files.push({
            name: attachement.name,
            path: `${ref}/${attachement.id}`
          })
        })
      })

      if (files.length) {
        const { data: signedUrls } = await this.$supabase.storage.from('project-annexes')
          .createSignedUrls(files.map(a => a.path), 3600)

        this.files = files.map((attachement, i) => {
          const signedData = signedUrls.find(o => o.path === attachement.path)

          return {
            name: attachement.name,
            link: signedData.signedUrl,
            path: attachement.path
          }
        })
      } else { this.files = [] }
    },
    async removeFile (file) {
      const { data: sectionsData } = await this.$supabase.from('pac_sections').select('attachements, ref').match({
        path: this.section.path,
        ref: this.gitRef
      })

      const attachements = sectionsData[0].attachements.filter(attachement => !file.path.includes(attachement.id))

      await this.$supabase.from('pac_sections').upsert({
        path: this.section.path,
        ref: this.gitRef,
        attachements
      })

      this.$emit('removed', file)
      this.dialog = false
    }
  }
}
</script>
