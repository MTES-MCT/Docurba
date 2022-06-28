<template>
  <v-card outlined tile color="g200" class="project-card">
    <v-card-title>{{ project.name }}</v-card-title>
    <v-card-subtitle>{{ project.docType }} - {{ placeName }}</v-card-subtitle>
    <v-card-text>
      <v-row>
        <v-col cols="4">
          <v-card flat tile>
            <v-card-subtitle class="text-h6 text--primary">
              Porté à connaissance
            </v-card-subtitle>
            <v-card-actions>
              <v-btn
                depressed
                color="primary"
                tile
                :to="`/projets/${project.id}/content`"
                nuxt
              >
                Consulter
                <v-icon class="ml-2">
                  {{ icons.mdiEye }}
                </v-icon>
              </v-btn>
              <v-btn
                depressed
                outlined
                color="primary"
                tile
                :loading="loadingPrint"
                @click.prevent.stop="printPAC"
              >
                Télécharger
                <v-icon class="ml-2">
                  {{ icons.mdiDownload }}
                </v-icon>
              </v-btn>
              <!-- <v-btn depressed outlined color="primary" tile>
                Charger
                <v-icon class="ml-2">
                  {{ icons.mdiUpload }}
                </v-icon>
              </v-btn> -->
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col cols="4">
          <v-card flat tile>
            <v-card-subtitle class="text-h6 text--primary">
              Jeux de données
            </v-card-subtitle>
            <v-card-actions>
              <v-btn
                depressed
                outlined
                color="primary"
                tile
                :to="`/projets/${project.id}/data?region=${project.region}`"
                nuxt
              >
                Consulter
                <v-icon class="ml-2">
                  {{ icons.mdiEye }}
                </v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col cols="4">
          <v-card flat tile>
            <v-card-subtitle class="text-h6 text--primary">
              Partage
            </v-card-subtitle>
            <v-card-text>
              List de partage
            </v-card-text>
            <v-card-actions>
              <v-dialog max-width="500px">
                <template #activator="{on}">
                  <v-btn
                    depressed
                    outlined
                    color="primary"
                    tile
                    v-on="on"
                    @click.prevent.stop
                  >
                    Partager
                    <v-icon class="ml-2">
                      {{ icons.mdiShare }}
                    </v-icon>
                  </v-btn>
                </template>
                <v-card>
                  <v-card-title>Partager le projet</v-card-title>
                  <v-card-text>
                    <ProjectsSharingForm :project="project" />
                  </v-card-text>
                </v-card>
              </v-dialog>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { mdiDownload, mdiEye, mdiUpload, mdiShare } from '@mdi/js'

export default {
  props: {
    project: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: { mdiDownload, mdiEye, mdiUpload, mdiShare },
      loadingPrint: false
    }
  },
  computed: {
    placeName () {
      return this.project.epci ? this.project.epci.label : this.project.towns[0].nom_commune
    }
  },
  methods: {
    async printPAC () {
      this.loadingPrint = true
      await this.$print(`/print/${this.project.id}`)
      this.loadingPrint = false
    }
  }
}
</script>

<style scoped>
.project-card {
  border-left: 6px solid #9a9aff !important;
}
</style>
