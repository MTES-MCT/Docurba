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
                      <validation-provider v-if="userData.poste === 'autre'" v-slot="{ errors }" name="Intitulé" rules="required">
                        <v-text-field
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
                        <span v-if="userData.poste !== 'be' && userData.poste !== 'agence_urba'">Quelle est votre collectivité ?</span>
                        <span v-else>Quelles collectivités accompagnez-vous ?*</span>
                      </div>
                    </v-col>
                    <v-col cols="12">
                      <VCollectivitesAutocomplete
                        v-model="selectedCollectivite"
                        large
                        :cols-dep="4"
                        :cols-town="8"
                        :input-props="{
                          filled: true
                        }"
                      />
                      <span v-if="userData.poste === 'be' || userData.poste === 'agence_urba'">
                        *Notez qu’il sera toujours possible d’élargir et modifier votre périmètre par la suite
                      </span>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12">
                      <v-checkbox
                        v-model="userData.optin"
                        label="Cochez cette case afin de recevoir nos lettres d'informations mensuelles pour ne rien louper aux dernières actualités de Docurba.
Promis, seul un contenu court et pertinent vous sera envoyé une fois par mois 🌎"
                        color="primary"
                        hide-details
                      />
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
                app
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
      selectedCollectivite: {},
      loading: false,
      userData: {
        email: this.$isDev ? `fabien+${this.$dayjs().format('DDMMYYhhmm')}@quantedsquare.com` : '',
        firstname: this.$isDev ? 'Test' : '',
        lastname: this.$isDev ? 'Test' : '',
        poste: '', // 'elu',
        other_poste: '', // 'test',
        tel: this.$isDev ? '0669487499' : '', // '0669487499',
        collectivite_id: '', // '45678'
        optin: false
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
      // console.log('signup')

      try {
        this.loading = true
        this.userData.other_poste = this.userData.other_poste ? [this.userData.other_poste] : null
        await axios({
          method: 'post',
          url: '/api/auth/signupCollectivite',
          data: {
            userData: {
              ...this.userData,
              collectivite_id: this.selectedCollectivite.code,
              departement: this.selectedCollectivite.departement
            },
            detailsCollectivite: this.selectedCollectivite,
            redirectTo: window.location.origin
          }
        })
        // console.log('ret: ', ret)
        this.$router.push({
          name: 'login-collectivites-explain',
          query: { collectivite_id: this.selectedCollectivite.code }
        })
      } catch (error) {
        // eslint-disable-next-line no-console
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
