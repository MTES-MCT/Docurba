<template>
  <v-dialog v-model="dialog">
    <template #activator="{ on: toolbarOn }">
      <v-tooltip bottom>
        <template #activator="{ on: tootlipOn }">
          <v-btn depressed tile icon v-on="{ ...toolbarOn, ...tootlipOn }">
            <v-icon>{{ icons.mdiNotePlusOutline }}</v-icon>
          </v-btn>
        </template>
        Ajouter un fichier
      </v-tooltip>
    </template>

    <v-card>
      <v-card-title>
        Ajouter une annexe à la section : {{ section.name }}
      </v-card-title>
      <v-card-text>
        <VFileDropzone class="drop-zone" @change="setFiles">
          <v-container>
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
          </v-container>
        </VFileDropzone>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn depressed tile color="primary" :loading="loading" @click="uploadFiles">
          Ajouter
        </v-btn>
        <v-btn depressed tile color="primary" outlined @click="dialog = false">
          Annuler
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mdiPlus, mdiNotePlusOutline } from '@mdi/js'
import { v4 as uuidv4 } from 'uuid'

export default {
  props: {
    section: {
      type: Object,
      required: true
    },
    gitRef: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiPlus,
        mdiNotePlusOutline
      },
      files: [],
      loading: false,
      dialog: false
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
        const { data: sectionsData } = await this.$supabase.from('pac_sections').select('attachements').match({
          path: this.section.path,
          ref: this.gitRef
        })

        const attachements = sectionsData[0] ? sectionsData[0].attachements : []

        for (let fileIndex = 0; fileIndex < this.files.length; fileIndex++) {
          const file = this.files[fileIndex]

          const fileId = uuidv4()

          attachements.push({
            id: fileId,
            name: file.name
          })

          // console.log(`${this.gitRef}/${this.section.path}/${fileId}`)

          await this.$supabase.storage
            .from('project-annexes')
            .upload(`${this.gitRef}/${fileId}`, file)
        }

        await this.$supabase.from('pac_sections').upsert({
          path: this.section.path,
          ref: this.gitRef,
          attachements
        })
      }

      this.$emit('upload')

      this.files = []
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
