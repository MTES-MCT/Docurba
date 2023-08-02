<template>
  <v-container class="fill-height">
    <v-row>
      <v-col cols="12">
        <div>
          <v-alert v-if="error" type="error">
            {{ error }}
          </v-alert>
          <div class="mb-2">
            <nuxt-link :to="{name: 'login'}">
              <v-icon small color="primary" class="mr-2">
                {{ icons.mdiArrowLeft }}
              </v-icon>
              Retour
            </nuxt-link>
          </div>
          <v-card flat class="border-light">
            <v-card-title>
              <div class="text-h1">
                Inscription Collectivité
              </div>
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <v-text-field v-model="userData.email" hide-details filled label="Email" />
                </v-col>
                <v-col cols="12">
                  <div class="text-h2">
                    Qui êtes vous ?
                  </div>
                </v-col>
                <v-col cols="6">
                  <v-text-field v-model="userData.firstname" hide-details filled label="Prénom" />
                </v-col>
                <v-col cols="6">
                  <v-text-field v-model="userData.lastname" hide-details filled label="Nom" />
                </v-col>
                <v-col cols="6">
                  <v-select v-model="userData.poste" :items="postes" hide-details filled label="Poste" />
                </v-col>
                <v-col>
                  <v-text-field
                    v-show="userData.poste === 'autre'"
                    v-model="userData.other_poste"
                    cols="6"
                    hide-details
                    filled
                    label="Intitulé"
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field v-model="userData.tel" hide-details filled label="Téléphone professionel" />
                </v-col>
                <v-col cols="12">
                  <div class="text-h2">
                    Quel est votre collectivité ?
                  </div>
                </v-col>
                <v-col cols="12">
                  <VCollectivitesAutocomplete
                    v-model="selectedCollectivite"
                    large
                    :cols-dep="4"
                    :cols-town="8"
                    :input-props="{
                      rules: [$rules.required]
                    }"
                  />
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn text tile color="primary" :to="{name: 'login-collectivites-signin'}">
                J'ai déjà un compte
              </v-btn>
              <v-btn depressed tile color="primary" :loading="loading" @click="signUp">
                Créer mon compte
              </v-btn>
            </v-card-actions>
          </v-card>
          <v-snackbar
            v-model="snackbar.val"
            :timeout="4000"
          >
            {{ snackbar.text }}
          </v-snackbar>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mdiArrowLeft } from '@mdi/js'
import axios from 'axios'

export default {
  name: 'SignupCollectivite',
  data () {
    return {
      icons: { mdiArrowLeft },
      postes: [
        { text: 'Bureau d\'étude', value: 'be' },
        { text: 'Elu(e)', value: 'elu' },
        { text: 'Technicien(ne) ou employé(e)', value: 'employe_mairie' },
        { text: 'Agence d\'urbanisme', value: 'agence_urba' },
        { text: 'Autre', value: 'autre' }
      ],
      selectedCollectivite: null,
      loading: false,
      userData: {
        firstname: 'jul',
        lastname: 'ler',
        email: 'test_jul@gmail.com',
        poste: 'elu',
        other_poste: 'test',
        tel: '0669487499',
        departement: '47',
        collectivite_id: '45678'
      },
      snackbar: {
        text: '',
        val: false
      },
      error: null
    }
  },
  methods: {
    async signUp () {
      try {
        this.loading = true
        const ret = await axios({
          method: 'post',
          url: '/api/auth/signupCollectivite',
          data: {
            userData: this.userData,
            redirectTo: window.location.origin
          }
        })
        console.log('ret: ', ret)
        // this.$router.push({ name: 'login-collectivites-explain' })
      } catch (error) {
        console.log(error)
        this.error = error
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
