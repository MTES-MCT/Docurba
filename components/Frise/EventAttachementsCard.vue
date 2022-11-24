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
              <p v-if="!displayedFiles.length" class="text-caption">
                Vous n’avez pas encore ajouté de fichier
              </p>
              <v-list v-else>
                <v-list-item v-for="file in displayedFiles" :key="file.id">
                  <v-list-item-title>{{ file.name }}</v-list-item-title>
                  <v-list-item-action class="mr-2">
                    <v-btn color="primary" outlined>
                      <v-icon>{{ icons.mdiDownload }}</v-icon>
                    </v-btn>
                  </v-list-item-action>
                  <v-list-item-action>
                    <v-btn color="primary" outlined>
                      <v-icon>{{ icons.mdiDelete }}</v-icon>
                    </v-btn>
                  </v-list-item-action>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </template>
  </VFileDropzone>
</template>

<script>
import { v4 as uuidv4 } from 'uuid'

import { mdiDownload, mdiDelete } from '@mdi/js'

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
      icons: {
        mdiDownload,
        mdiDelete
      },
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
    displayedFiles: {
      deep: true,
      handler () {
        this.$emit('input', [...this.files])
      }
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
