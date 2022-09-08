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
    files: {
      type: Array,
      required: true
    },
    small: {
      type: Boolean,
      default: false
    },
    editable: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      dialog: false,
      selectedFile: {}
    }
  },
  methods: {
    openDialog (file) {
      this.dialog = true
      this.selectedFile = file
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
