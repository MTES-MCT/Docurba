<template>
  <v-row>
    <v-col cols="12">
      <v-chip
        v-for="file in files"
        :key="file.name"
        class="mr-1 mb-1"
        color="primary"
        :href="file.url"
        target="_blank"
        :small="small"
        :close="editable && file.editable"
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
          <v-btn depressed tile color="primary" @click="removeFile(selectedFile)">
            Supprimer
          </v-btn>
          <v-btn depressed tile text color="primary" @click="dialog = false">
            Annuler
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
      type: String,
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
    attachementsFolders: {
      type: Array,
      default () { return [] }
    }
  },
  data () {
    return {
      files: [],
      dialog: false,
      selectedFile: {}
    }
  },
  watch: {
    'section.path' () {
      this.fetchAttachements()
    }
  },
  mounted () {
    this.fetchAttachements()
  },
  methods: {
    openDialog (file) {
      this.dialog = true
      this.selectedFile = file
    },
    fetchAttachements () {
      this.attachements = []

      this.attachementsFolders.forEach((folder) => {
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
            // File is not editable if user is working on project and file was uploaded for the departmenet.
            file.editable = this.editable ? (folder === this.section.project_id) : true

            this.files.push(file)
          } else {
            // console.log('fileError', filePath)
            // console.log(data, fileError)
          }
        }
      }
    },
    removeFile (file) {
      this.$supabase.storage.from('project-annexes')
        .remove([file.path])

      this.$emit('removed', file)
      this.dialog = false
    }
  }
}
</script>
