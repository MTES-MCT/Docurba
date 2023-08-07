<template>
  <validation-observer ref="observerSignupCollectivite" v-slot="{ handleSubmit }">
    <form @submit.prevent="handleSubmit(signUp)">
      <v-container class="fill-height">
        <v-row>
          <v-col cols="12">
            <div>
              <v-alert v-if="error" type="info">
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
                      <validation-provider v-slot="{ errors }" name="Email" rules="required|email">
                        <v-text-field v-model="userData.email" :error-messages="errors" filled label="Email" />
                      </validation-provider>
                    </v-col>
                    <v-col cols="12">
                      <div class="text-h2">
                        Qui êtes vous ?
                      </div>
                    </v-col>
                    <v-col cols="6">
                      <validation-provider v-slot="{ errors }" name="Prénom" rules="required">
                        <v-text-field v-model="userData.firstname" :error-messages="errors" filled label="Prénom" />
                      </validation-provider>
                    </v-col>
                    <v-col cols="6">
                      <validation-provider v-slot="{ errors }" name="Nom" rules="required">
                        <v-text-field v-model="userData.lastname" :error-messages="errors" filled label="Nom" />
                      </validation-provider>
                    </v-col>
                    <v-col cols="6">
                      <validation-provider v-slot="{ errors }" name="Poste" rules="required">
                        <v-select
                          v-model="userData.poste"
                          :error-messages="errors"
                          :items="postes"
                          filled
                          label="Poste"
                        />
                      </validation-provider>
                    </v-col>
                    <v-col>
                      <validation-provider v-slot="{ errors }" name="Intitulé" rules="required">
                        <v-text-field
                          v-show="userData.poste === 'autre'"
                          v-model="userData.other_poste"
                          cols="6"
                          :error-messages="errors"
                          filled
                          label="Intitulé"
                        />
                      </validation-provider>
                    </v-col>
                    <v-col cols="6">
                      <validation-provider v-slot="{ errors }" name="Téléphone professionel" rules="required">
                        <v-text-field v-model="userData.tel" :error-messages="errors" filled label="Téléphone professionel" />
                      </validation-provider>
                    </v-col>
                    <v-col cols="12">
                      <div class="text-h2">
                        Quelle est votre collectivité ?
                      </div>
                    </v-col>
                    <v-col cols="12">
                      <validation-provider v-slot="{ errors }" name="Collectivité" rules="requiredCollectivite">
                        <VCollectivitesAutocomplete
                          v-model="selectedCollectivite"
                          :error-messages="errors"
                          large
                          :cols-dep="4"
                          :cols-town="8"
                        />
                      </validation-provider>
                    </v-col>
                  </v-row>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn text tile color="primary" :to="{name: 'login-collectivites-signin'}">
                    J'ai déjà un compte
                  </v-btn>
                  <v-btn depressed tile color="primary" :loading="loading" type="submit">
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
    </form>
  </validation-observer>
</template>

<script>
import { mdiArrowLeft } from '@mdi/js'
import axios from 'axios'

import FormInput from '@/mixins/FormInput.js'

export default {
  name: 'SignupCollectivite',
  mixins: [FormInput],
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
        email: 'testjulien1@yopmail.com',
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
        this.$router.push({ name: 'login-collectivites-explain' })
      } catch (error) {
        console.log(error)
        this.error = error.response.data.message
        this.$vuetify.goTo(0)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
