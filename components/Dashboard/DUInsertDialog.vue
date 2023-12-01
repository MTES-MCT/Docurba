<template>
  <v-dialog v-model="isOpen" max-width="800px">
    <v-card>
      <v-card-title>Création d'un nouveau document d'urbanisme</v-card-title>
      <v-card-text>
        <v-form>
          <v-row>
            <v-col cols="12">
              <v-autocomplete
                v-model="selectedCollectivite"
                hide-details
                :items="collectivites"
                item-text="intitule"
                return-object
                filled
                placeholder="Commune ou EPCI"
              />
            </v-col>
            <v-col v-if="!!selectedCollectivite" cols="12">
              <v-text-field
                v-model="newProject.name"
                filled
                hide-details
                label="Nom du document"
              />
            </v-col>
            <v-col v-if="!!selectedCollectivite" cols="12">
              <v-select
                v-model="newProject.doc_type"
                :items="docTypes"
                label="Type de document"
                filled
                hide-details
              />
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" outlined tile @click="close">
          Annuler
        </v-btn>
        <v-btn color="primary" :loading="saving" tile depressed @click="insertProject">
          Ajouter
        </v-btn>
      </v-card-actions>
    </v-card>
    <v-snackbar
      v-model="snackbar"
    >
      Une erreur est survenue à la creation de votre document.
      <template #action>
        <v-btn
          text
          @click="snackbar = false"
        >
          Fermer
        </v-btn>
      </template>
    </v-snackbar>
  </v-dialog>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    value: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      saving: false,
      snackbar: false,
      collectivites: [],
      selectedCollectivite: null,
      // This follow the keys of project table.
      newProject: {
        name: '',
        doc_type: '',
        owner: this.$user.id,
        PAC: [] // this should be removede when collumn is moved to a PAC table,
      }
    }
  },
  computed: {
    isEpci () {
      return this.selectedCollectivite.code.length === 9
    },
    towns () {
      if (this.selectedCollectivite) {
        return this.selectedCollectivite.communes ? this.selectedCollectivite.communes : [this.selectedCollectivite]
      } else {
        return []
      }
    },
    docTypes () {
      return this.isEpci
        ? [
            'PLUi', 'PLUi-H', 'PLUi-D', 'PLUi-HD'
          ]
        : [
            'CC', 'PLU'
          ]
    },
    isOpen: {
      set (val) {
        this.$emit('input', val)
      },
      get () {
        return this.value
      }
    }
  },
  mounted () {
    this.fetchCollectivites()
  },
  methods: {
    async insertProject () {
      this.saving = true

      const project = Object.assign({
        collectivite_id: this.selectedCollectivite.code,
        towns: [...this.towns],
        epci: this.isEpci,
        region: this.selectedCollectivite.regionCode,
        trame: this.selectedCollectivite.departementCode
      }, this.newProject)

      const { data: projects, error } = await this.$supabase.from('projects')
        .insert(project).select()

      if (!error) {
        const project = projects[0]

        await axios({
          method: 'post',
          url: `/api/trames/projects/dept-${this.$options.filters.deptToRef(this.selectedCollectivite.departementCode)}`,
          data: {
            userId: this.$user.id,
            projectId: project.id
          }
        })

        this.isOpen = false
        this.$emit('insert')
      } else {
        this.snackbar = true
      }

      this.saving = false
    },
    async fetchCollectivites () {
      const departement = this.$user.profile.departement

      if (departement) {
        const { data: communes } = await axios('/api/geo/communes?departementCode=01')
        const { data: intercomunalites } = await axios('/api/geo/intercommunalites?departementCode=01')

        this.collectivites = [{ header: 'ECPI' }, ...intercomunalites, { divider: true }, { header: 'Communes' }, ...communes]
      }
    },
    close () {
      this.$emit('input', false)
    }
  }
}
</script>
