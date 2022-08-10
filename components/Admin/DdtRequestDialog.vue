<template>
  <v-dialog v-model="dialog" width="500">
    <v-card>
      <v-card-title>Demande d'accès DDT</v-card-title>
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
        <v-btn color="primary" @click="makeDDTRequest">
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
        await this.$supabase.from('admin_users_dept').insert([{
          role: 'user',
          dept: this.selectedDepartement.code_departement,
          user_id: this.$user.id,
          user_email: this.$user.email
        }])

        console.log(this.$user)

        await axios({
          url: '/api/slack/notify/admin',
          method: 'post',
          data: {
            userData: {
              email: this.$user.email,
              firstname: this.$user.user_metadata.firstname,
              lastname: this.$user.user_metadata.lastname,
              dept: this.selectedDepartement
            }
          }
        })
      }

      this.dialog = false
    }
  }
}
</script>
