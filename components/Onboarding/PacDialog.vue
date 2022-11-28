<template>
  <v-dialog v-model="dialog" max-width="1000px">
    <template #activator="{on}">
      <v-snackbar v-model="snackbar" absolute>
        Votre demande à été transmise.
      </v-snackbar>

      <v-btn depressed tile color="primary" v-on="on">
        Obtenir mon PAC
      </v-btn>
    </template>
    <v-card>
      <v-card-title>Obtenir mon PAC</v-card-title>
      <v-card-text>
        <v-row>
          <v-col v-if="!$user.id" cols="6">
            <OnboardingSignupForm v-model="userData" />
          </v-col>
          <v-col :cols="$user.id ? 12 : 6">
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
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn depressed tile color="primary" :loading="loading" @click="loginAndcreateProject">
          Transmettre ma demande
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios'
import regions from '@/assets/data/Regions.json'

export default {
  data () {
    return {
      userData: {},
      projectData: {
        name: '',
        doc_type: ''
      },
      selectedTown: {},
      dialog: false,
      loading: false,
      snackbar: false
    }
  },
  methods: {
    async loginAndcreateProject () {
      this.loading = true

      const { error: signInErr } = await this.$auth.signIn(this.userData)

      if (signInErr && signInErr.message === 'Invalid login credentials') {
        await this.$auth.signUp(this.userData)
      }

      axios({
        url: '/api/admin/pac',
        method: 'post',
        data: {
          userData: this.$user,
          pacData: Object.assign({
            town: this.selectedTown,
            region: regions.find(r => r.name === this.selectedTown.nom_region).iso
          }, this.projectData)
        }
      })

      this.snackbar = true
      this.loading = false
      this.dialog = false
    }
  }
}
</script>
