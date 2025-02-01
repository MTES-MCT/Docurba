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

          <v-card v-if="!forgotPassword" flat class="border-light">
            <validation-observer ref="observerSignInEtat" v-slot="{ handleSubmit }">
              <form @submit.prevent="handleSubmit(signIn)">
                <v-card-title>
                  <div class="text-h1">
                    Connexion agent de l'Etat
                  </div>
                </v-card-title>
                <v-card-text>
                  <v-row justify="end">
                    <v-col cols="12">
                      <validation-provider v-slot="{ errors }" name="E-mail" rules="required|email">
                        <v-text-field v-model="email" :error-messages="errors" filled label="Email" />
                      </validation-provider>
                    </v-col>
                    <v-col cols="12">
                      <InputsPasswordTextField v-model="password" />
                    </v-col>
                    <v-spacer />
                    <v-col cols="auto" class="pt-0">
                      <a href="#" class="primary--text" @click="forgotPassword = true">Mot de passe oublié ? Cliquez ici</a>
                    </v-col>
                  </v-row>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn class=" no-text-transform" outlined tile color="primary" :to="{name: 'login-ddt-signup'}">
                    Pas de compte ? Créez en un
                  </v-btn>
                  <v-btn depressed tile color="primary" type="submit">
                    Se connecter
                  </v-btn>
                </v-card-actions>
              </form>
            </validation-observer>
          </v-card>

          <v-card v-else flat class="border-light">
            <validation-observer ref="observerResetPassword" v-slot="{ handleSubmit }">
              <form @submit.prevent="handleSubmit(sendResetPassword)">
                <v-card-title>
                  <div class="text-h1">
                    Récupération de mot de passe
                  </div>
                </v-card-title>
                <v-card-text>
                  <v-row justify="end">
                    <v-col cols="12">
                      <validation-provider v-slot="{ errors }" name="E-mail" rules="required|email">
                        <v-text-field v-model="email" :error-messages="errors" filled label="Email" />
                      </validation-provider>
                    </v-col>
                  </v-row>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn outlined tile color="primary" @click="forgotPassword = false">
                    Retour
                  </v-btn>
                  <v-btn depressed tile color="primary" @click="sendResetPassword">
                    Envoyer
                  </v-btn>
                </v-card-actions>
              </form>
            </validation-observer>
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
</template>

<script>
import { mdiEye, mdiEyeOff, mdiArrowLeft } from '@mdi/js'

import axios from 'axios'
import FormInput from '@/mixins/FormInput.js'

export default {
  name: 'SignInDdt',
  mixins: [FormInput],
  data () {
    return {
      icons: {
        mdiEye,
        mdiEyeOff,
        mdiArrowLeft
      },
      forgotPassword: false,
      showPassword: false,
      email: '',
      password: '',
      snackbar: {
        text: '',
        val: false
      },
      error: null
    }
  },
  computed: {
    trameRef () {
      const scopes = { ddt: 'dept', dreal: 'region' }
      const poste = this.$user.profile.poste
      const code = poste === 'ddt' ? this.$user.profile.departement : this.$user.profile.region

      return `${scopes[poste]}-${code}`
    }
  },
  methods: {
    async signIn () {
      try {
        const { error } = await this.$auth.signIn({
          email: this.email,
          password: this.password
        })
        if (error) { throw error }
      } catch (error) {
        console.log('error: ', error)
        this.error = 'Email ou mot de passe incorrect.'
      }
    },
    async sendResetPassword () {
      try {
        await axios({
          method: 'post',
          url: '/api/auth/password',
          data: {
            email: this.email,
            redirectTo: window.location.origin
          }
        })

        this.snackbar = {
          val: true,
          text: `Un email de changement de mot de passe à été envoyé à ${this.userData.email}`
        }
        this.forgotPassword = false
      } catch (error) {
        console.log(error)
      }
    }
  }
}
</script>
