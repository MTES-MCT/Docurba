<template>
  <v-dialog v-model="dialog" width="500">
    <v-card>
      <v-card-title>Demande d'accès DDT/DEAL</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12">
            <v-autocomplete
              v-model="selectedDepartement"
              :items="departements"
              label="Departement"
              hide-details
              filled
              return-object
            />
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn depressed tile color="primary" @click="makeDDTRequest">
          Envoyer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios'
import departements from '@/assets/data/departements-france.json'

export default {
  props: {
    value: {
      type: Boolean,
      default: false
    }
  },
  data () {
    const enrichedDepartements = departements.map(d => Object.assign({
      text: `${d.nom_departement} - ${d.code_departement}`
    }, d))

    return {
      departements: enrichedDepartements,
      selectedDepartement: null
    }
  },
  computed: {
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
    async makeDDTRequest () {
      if (this.selectedDepartement) {
        await this.$supabase.from('github_ref_roles').insert([{
          role: 'user',
          ref: `dept-${this.selectedDepartement.code_departement}`,
          user_id: this.$user.id
        }])

        await axios({
          url: '/api/slack/notify/admin',
          method: 'post',
          data: {
            userData: {
              email: this.$user.email,
              firstname: this.$user.user_metadata.firstname,
              lastname: this.$user.user_metadata.lastname,
              dept: this.selectedDepartement,
              id: this.$user.id
            }
          }
        })
      }

      this.dialog = false
    }
  }
}
</script>
