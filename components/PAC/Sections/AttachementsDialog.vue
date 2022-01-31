<template>
  <v-dialog v-model="dialog" width="800px">
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
        <v-tab disabled>
          Data
        </v-tab>
      </v-tabs>
      <v-tabs-items v-model="ressourcesTab">
        <v-tab-item>
          <VFileDropzone class="drop-zone" @change="setFiles">
            <v-card-text>
              <v-row justify="center">
                <v-col v-if="!files.length" cols="3">
                  <v-sheet color="g100" height="182px" class="d-flex align-center justify-center">
                    <v-icon large color="primary">
                      {{ icons.mdiPlus }}
                    </v-icon>
                  </v-sheet>
                </v-col>
                <v-col
                  v-for="(file, i) in files"
                  :key="`${file.name}--${i}`"
                  cols="3"
                >
                  <v-sheet
                    elevation="1"
                    class="pa-2"
                    height="182px"
                  >
                    {{ file.name }}
                  </v-sheet>
                </v-col>
              </v-row>
            </v-card-text>
          </VFileDropzone>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary" :loading="loading" @click="uploadFiles">
              Ajouter
            </v-btn>
            <v-btn color="primary" outlined @click="dialog.value = false">
              Annuler
            </v-btn>
          </v-card-actions>
        </v-tab-item>
        <v-tab-item>
          <v-card-text>
            Data
          </v-card-text>
        </v-tab-item>
      </v-tabs-items>
    </v-card>
  </v-dialog>
</template>

<script>
import { mdiPlus, mdiPaperclip } from '@mdi/js'

export default {
  props: {
    section: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiPlus,
        mdiPaperclip
      },
      ressourcesTab: 0,
      files: [],
      loading: false,
      dialog: false
    }
  },
  computed: {
    folder () {
      return this.section.project_id || this.section.dept
    }
  },
  methods: {
    setFiles (files) {
      // console.log('change files', files)
      this.files = files
    },
    async uploadFiles () {
      // console.log(this.files)
      this.loading = true

      if (this.files.length) {
        // this.files.forEach((file) => {
        //   console.log(file)
        // })

        // console.log(this.files[0], this.section)

        for (let fileIndex = 0; fileIndex < this.files.length; fileIndex++) {
          const file = this.files[fileIndex]

          await this.$supabase.storage
            .from('project-annexes')
            .upload(`/${this.folder}${this.section.path}/${file.name}`, file)
        }
      }

      this.$emit('upload')

      this.loading = false
      this.dialog = false
    }
  }
}
</script>

<style scoped>
 .drop-zone {
   cursor: pointer;
 }
</style>
