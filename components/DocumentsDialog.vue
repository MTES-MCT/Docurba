<template>
  <v-dialog v-model="dialog" width="500">
    <v-card>
      <v-card-title>Mes documents</v-card-title>
      <v-card-text>
        <v-tabs-items v-model="modalState">
          <v-tab-item id="list">
            <v-list height="400px" class="overflow-auto">
              <v-list-item
                v-for="project in projects"
                :key="project.id"
                :to="`/projets/${project.id}/content`"
                nuxt
                two-line
                @click="$emit('input', false)"
              >
                <v-list-item-content>
                  <v-list-item-title>{{ project.name }}</v-list-item-title>
                  <v-list-item-subtitle>{{ project.docType }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
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
                <VDocumentSelect v-model="projectData.docType" label="Type de document" />
              </v-col>
              <v-col cols="12">
                <VTownAutocomplete v-model="selectedTown" />
                <!-- <VRegionAutocomplete v-model="projectData.region" label="Votre region" return-iso /> -->
              </v-col>
            </v-row>
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn v-show="modalState === 'list'" color="primary" @click="modalState = 'create'">
          Nouveau
        </v-btn>
        <v-btn v-show="modalState === 'create'" color="primary" outlined @click="modalState = 'list'">
          Annuler
        </v-btn>
        <v-btn
          v-show="modalState === 'create'"
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

export default {
  name: 'DocumentsDialog',
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
        docType: '',
        region: ''
      },
      selectedTown: {},
      projects: [],
      loading: false
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
  async mounted () {
    const { data: projects, error } = await this.$supabase.from('projects').select('id, name, docType, created_at').eq('owner', this.$user.id)

    if (!error) {
      this.projects = projects
    } else {
      // eslint-disable-next-line no-console
      console.log(error)
    }
  },
  methods: {
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

      const { data, error } = await this.$supabase.from('projects').insert([newProject])

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
