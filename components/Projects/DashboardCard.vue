<template>
  <v-card outlined tile color="g200" class="project-card">
    <v-card-title>
      {{ projectData.name }}
      <span />
      <v-spacer />
      <v-dialog v-if="!shared" width="500px">
        <template #activator="{on}">
          <v-btn
            depressed
            tile
            icon
            color="primary"
            v-on="on"
            @click.prevent.stop
          >
            <v-icon>
              {{ icons.mdiPencil }}
            </v-icon>
          </v-btn>
        </template>
        <template #default="dialog">
          <ProjectsProjectCardForm :project="projectData" @cancel="dialog.value = false">
            <template #title>
              Modifier le projet
            </template>
          </ProjectsProjectCardForm>
        </template>
      </v-dialog>
    </v-card-title>
    <v-card-subtitle>{{ projectData.doc_type }} - {{ placeName }}</v-card-subtitle>
    <v-card-text>
      <v-row>
        <v-col cols="4">
          <v-card flat tile>
            <v-card-subtitle class="text-h6 text--primary">
              Porter à connaissance
            </v-card-subtitle>
            <v-card-actions>
              <v-btn
                depressed
                tile
                color="primary"
                :to="`/documents/projet-${projectData.id}/pac`"
                nuxt
              >
                Consulter
                <v-icon class="ml-2">
                  {{ icons.mdiEye }}
                </v-icon>
              </v-btn>
              <v-btn
                v-if="projectData.trame && editor"
                depressed
                tile
                outlined
                color="primary"
                :to="`/trames/projet-${projectData.id}`"
                nuxt
              >
                Modifier
                <v-icon class="ml-2">
                  {{ icons.mdiPencil }}
                </v-icon>
              </v-btn>
              <v-btn
                v-if="!projectData.trame && editor"
                depressed
                tile
                outlined
                color="primary"
                :loading="loadingUpload"
                @click="$refs['pacInput'].click()"
              >
                Charger
                <v-icon class="ml-2">
                  {{ icons.mdiUpload }}
                </v-icon>
              </v-btn>
              <input ref="pacInput" class="d-none" type="file" accept=".pdf" @change="uploadPAC">
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col cols="4">
          <!-- <v-card flat tile>
            <v-card-subtitle class="text-h6 text--primary">
              Jeux de données
            </v-card-subtitle>
            <v-card-actions>
              <v-btn
                depressed
                tile
                outlined
                color="primary"
                :to="`/projets/${projectData.id}/data?region=${projectData.region}`"
                nuxt
              >
                Consulter
                <v-icon class="ml-2">
                  {{ icons.mdiEye }}
                </v-icon>
              </v-btn>
            </v-card-actions>
          </v-card> -->
          <v-card flat tile>
            <v-card-subtitle class="text-h6 text--primary">
              Frise d'évènements
            </v-card-subtitle>
            <v-card-actions>
              <v-btn
                depressed
                tile
                outlined
                color="primary"
                :to="`/projets/${projectData.id}/frise`"
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
            <v-card-text v-if="nbSharings">
              {{ nbSharings }} email{{ nbSharings > 1 ? 's ont' : ' a' }} accès à ce projet
            </v-card-text>
            <v-card-actions>
              <v-dialog max-width="600px">
                <template #activator="{on}">
                  <v-btn
                    v-if="!shared"
                    depressed
                    tile
                    outlined
                    color="primary"
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
                    <ProjectsSharingForm :project="projectData" />
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
import { mdiDownload, mdiEye, mdiUpload, mdiShare, mdiPencil } from '@mdi/js'

export default {
  props: {
    project: {
      type: Object,
      required: true
    },
    sharing: {
      type: Object,
      default () {
        return {}
      }
    }
  },
  data () {
    return {
      projectData: Object.assign({}, this.project),
      projectSubscription: null,
      icons: { mdiDownload, mdiEye, mdiUpload, mdiShare, mdiPencil },
      loadingPrint: false,
      loadingUpload: false,
      nbSharings: 0
    }
  },
  computed: {
    placeName () {
      return this.project.epci ? this.project.epci.intitule : this.project.towns[0].intitule
    },
    shared () {
      return this.project.owner !== this.$user.id
    },
    editor () {
      return !this.shared || (this.sharing ? this.sharing.role === 'write' : false)
    }
  },
  async mounted () {
    const { count: sharings, error } = await this.$supabase.from('projects_sharing').select('id', {
      count: 'exact',
      head: true
    }).eq('project_id', this.project.id)

    this.projectSubscription = this.$supabase
      .channel(`public:projects:id=eq.${this.project.id}`)
      .on('postgres_changes', {
        event: 'UPDATE',
        schema: 'public',
        table: 'projects',
        filter: `id=eq.${this.project.id}`
      }, (payload) => {
        // console.log('Change received on project', payload)
        Object.assign(this.projectData, payload.new)
      })
      .subscribe()

    if (!error) {
      this.nbSharings = sharings
    }
  },
  beforeDestroy () {
    this.$supabase.removeChannel(this.projectSubscription)
  },
  methods: {
    async printPAC () {
      this.loadingPrint = true
      await this.$print(`/print/${this.project.id}`)
      this.loadingPrint = false
    },
    async uploadPAC () {
      const pac = this.$refs.pacInput.files[0]

      this.loadingUpload = true

      if (pac) {
        await this.$supabase.storage
          .from('projects-pac')
          .upload(`${this.project.id}/pac.pdf`, pac)
      }

      this.loadingUpload = false
    }
  }
}
</script>

<style scoped>
.project-card {
  border-left: 6px solid #9a9aff !important;
}
</style>
