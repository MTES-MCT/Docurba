<template>
  <v-dialog v-model="isOpen" max-width="800px">
    <v-card>
      <v-card-title>Création d'un nouveau document d'urbanisme</v-card-title>
      <v-card-text>
        <v-form>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="newProject.name"
                filled
                hide-details
                label="Nom du document"
              />
            </v-col>
            <v-col cols="12">
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
    },
    collectivite: {
      type: Object,
      required: true
    }
  },
  data () {
    // console.log('DUInsertDialog collectivite', this.collectivite)

    const collectiviteId = this.collectivite.code
    const isEpci = collectiviteId.length === 9
    const towns = isEpci ? this.collectivite.communes : [this.collectivite]

    return {
      saving: false,
      snackbar: false,
      isEpci,
      // This follow the keys of project table.
      newProject: {
        name: '',
        doc_type: '',
        collectivite_id: collectiviteId,
        owner: this.$user.id,
        towns, // idealy this is done automatically by the DB
        epci: isEpci ? this.collectivite : null, // Same here, this should be made by the DB
        region: this.collectivite.regionCode, // I think this collumn could be removed.
        PAC: [], // this should be removede when collumn is moved to a PAC table,
        trame: this.collectivite.departementCode // This should go in the PAC table as well
        // towns_insee: null // No other values in DB for now ?
      }
    }
  },
  computed: {
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
  methods: {
    async insertProject () {
      this.saving = true

      const { data: projects, error } = await this.$supabase.from('projects')
        .insert(this.newProject).select()

      if (!error) {
        const project = projects[0]

        await axios({
          method: 'post',
          url: `/api/trames/projects/dept-${this.$options.filters.deptToRef(this.collectivite.departementCode)}`,
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
    close () {
      this.$emit('input', false)
    }
  }
}
</script>
