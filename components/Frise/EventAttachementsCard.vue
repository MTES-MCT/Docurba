<template>
  <VFileDropzone drop-only @change="addFiles">
    <template #default="{openFiles}">
      <v-card outlined flat>
        <v-card-title class="text-h3 black--text">
          Éléments facultatifs
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <h3 class="text-6 black--text">
                Ajouter un fichier
              </h3>
            </v-col>
            <v-col cols="6">
              <p class="text-caption">
                Vous pouvez déposer plusieurs fichiers.
              </p>
              <v-btn depressed tile @click="openFiles">
                Parcourir...
              </v-btn>
            </v-col>
            <v-col cols="6">
              <p v-if="!files.length" class="text-caption">
                Vous n’avez pas encore ajouté de fichier
              </p>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </template>
  </VFileDropzone>
</template>

<script>
import { v4 as uuidv4 } from 'uuid'

export default {
  model: {
    prop: 'attachements',
    event: 'input'
  },
  props: {
    attachements: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      files: this.attachements.map((file) => {
        return Object.assign({ state: 'old' }, file)
      })
    }
  },
  computed: {
    displayedFiles () {
      return this.files.filter((file) => {
        return file.state !== 'removed'
      })
    }
  },
  watch: {
    displayedFiles () {
      this.$emit('input', [...this.files])
    }
  },
  methods: {
    addFiles (files) {
      // console.log('HandleFiles', files)

      for (const file of files) {
        this.files.push({
          id: uuidv4(),
          name: file.name,
          file,
          state: 'new'
        })
      }
    }
  }
}
</script>
