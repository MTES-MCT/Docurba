<template>
  <VFileDropzone drop-only @change="addFiles">
    <template #default="{openFiles}">
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
                <v-btn
                  color="primary"
                  :lodaing="dowloading.includes(file.id)"
                  outlined
                  @click="downloadFile(file)"
                >
                  <v-icon>{{ icons.mdiDownload }}</v-icon>
                </v-btn>
                <a :ref="`file-${file.id}`" class="d-none" :download="file.name" />
              </v-list-item-action>
              <v-list-item-action>
                <v-dialog max-width="350px">
                  <template #activator="{on}">
                    <v-btn color="primary" outlined v-on="on">
                      <v-icon>{{ icons.mdiDelete }}</v-icon>
                    </v-btn>
                  </template>
                  <template #default="dialog">
                    <v-card>
                      <v-card-title>Supprimer {{ file.name }} ?</v-card-title>
                      <v-card-text>
                        Après la sauvegarde de vos modifications, cette pièce jointe sera définitivement supprimée.
                      </v-card-text>
                      <v-card-actions>
                        <v-spacer />
                        <v-btn color="primary" outlined tile @click="dialog.value = false">
                          Annuler
                        </v-btn>
                        <v-btn color="primary" tile @click="dialog.value = false || removeFile(file)">
                          Supprimer
                        </v-btn>
                      </v-card-actions>
                    </v-card>
                  </template>
                </v-dialog>
              </v-list-item-action>
            </v-list-item>
          </v-list>
        </v-col>
      </v-row>
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
    },
    projectId: {
      type: String,
      default () {
        return this.$route.params.projectId
      }
    },
    eventId: {
      type: String,
      default () {
        return this.$route.params.eventId
      }
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
      }),
      dowloading: []
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
    },
    removeFile (file) {
      file.state = 'removed'
    },
    async downloadFile (file) {
      this.dowloading.push(file.id)

      const { data } = await this.$supabase.storage.from('doc-events-attachements')
        .download(`${this.projectId}/${this.eventId}/${file.id}`)

      const link = this.$refs[`file-${file.id}`][0]
      link.href = URL.createObjectURL(data)
      link.click()

      this.dowloading = this.dowloading.filter(id => id !== file.id)
    }
  }
}
</script>
