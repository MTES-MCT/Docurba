<template>
  <v-dialog v-model="dialog" width="500">
    <v-card>
      <v-card-title>Mes documents</v-card-title>
      <v-card-text>
        <v-tabs-items v-model="modalState">
          <v-tab-item id="list">
            <v-list max-height="400px" class="overflow-auto">
              <ProjectsProjectListItem
                v-for="project in projects"
                :key="project.id"
                :project="project"
                shareable
                @share="shareProject(project)"
              />
            </v-list>
            <v-card-subtitle v-show="sharedProjects.length">
              Documents partagés avec moi
            </v-card-subtitle>
            <v-list v-show="sharedProjects.length">
              <ProjectsProjectListItem
                v-for="project in sharedProjects"
                :key="project.id"
                :project="project"
                @share="shareProject(project)"
              />
            </v-list>
          </v-tab-item>
          <v-tab-item id="create">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="projectData.name"
                  filled
                  hide-details
                  label="Nom du projet"
                />
              </v-col>
              <v-col cols="12">
                <VDocumentSelect v-model="projectData.doc_type" label="Type de document" />
              </v-col>
              <v-col cols="12">
                <VTownAutocomplete v-model="selectedTown" />
                <!-- <VRegionAutocomplete v-model="projectData.region" label="Votre region" return-iso /> -->
              </v-col>
            </v-row>
          </v-tab-item>
          <v-tab-item id="share">
            <ProjectsSharingForm :project="selectedProject" />
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn v-show="modalState === 'list'" depressed tile color="primary" @click="modalState = 'create'">
          Nouveau
        </v-btn>
        <v-btn
          v-show="modalState !== 'list'"
          depressed
          tile
          color="primary"
          outlined
          @click="modalState = 'list'"
        >
          Retour
        </v-btn>
        <v-btn
          v-show="modalState === 'create'"
          depressed
          tile
          :loading="loading"
          color="primary"
          @click="createNewProject"
        >
          Créer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import regions from '@/assets/data/Regions.json'

import projectsList from '@/mixins/projectsList.js'

export default {
  name: 'DocumentsDialog',
  mixins: [projectsList],
  props: {
    value: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      modalState: 'list',
      projectData: {
        name: '',
        doc_type: '',
        region: ''
      },
      selectedTown: {},
      loading: false,
      selectedProject: {}
    }
  },
  computed: {
    selectedRegion () {
      const region = regions.find(r => r.name === this.selectedTown.nom_region)

      return region.iso
    },
    dialog: {
      get () {
        return this.value || false
      },
      set (val) {
        this.$emit('input', val)
      }
    }
  },
  methods: {
    shareProject (project) {
      this.selectedProject = project
      this.modalState = 'share'
    },
    async createNewProject () {
      this.loading = true

      const PAC = await this.$content('PAC', {
        deep: true
        // text: true
      }).fetch()

      // console.log(PAC)

      const newProject = Object.assign({
        owner: this.$user.id,
        PAC
      }, this.projectData, {
        region: this.selectedRegion
      })

      const { data, error } = await this.$supabase.from('projects').insert([newProject]).select()

      this.$analytics({
        category: 'pac',
        name: 'create_project',
        value: this.projectData.name
      })

      if (!error && data && data[0]) {
        const project = data[0]
        this.projects.push(project)
        this.dialog = false
        this.$router.push(`/projets/${project.id}/content`)
      } else {
        // eslint-disable-next-line no-console
        console.log(error)
      }

      this.loading = false
    }
  }
}
</script>
