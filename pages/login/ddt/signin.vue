<template>
  <v-container class="fill-height">
    <v-row>
      <v-col cols="12">
        <div>
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
                Connexion agent de l'Etat
              </div>
            </v-card-title>

            <v-card-text>
              <v-form ref="loginForm" v-model="isLoginValid">
                <v-row justify="end">
                  <v-col cols="12">
                    <v-text-field v-model="userData.email" :rules="[$rules.required]" hide-details filled label="Email" />
                  </v-col>
                  <v-col v-show="!forgotPassword" cols="12">
                    <InputsPasswordTextField v-model="userData.password" />
                  </v-col>
                  <v-col v-if="error && error.status === 400" cols="12">
                    <span class="error--text">Email ou mot de passe incorrecte.</span>
                  </v-col>
                  <v-spacer />
                  <v-col v-show="!forgotPassword" cols="auto">
                    <v-btn depressed tile text small @click="sendResetPassword">
                      Mot de passe oublié ?
                    </v-btn>
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>

            <v-card-actions>
              <v-spacer />
              <v-btn v-show="!forgotPassword" outlined tile color="primary" :to="{name: 'login-ddt-signup'}">
                Pas de compte ? Créez en un
              </v-btn>
              <v-btn v-show="!forgotPassword" depressed tile color="primary" @click="signIn()">
                Se connecter
              </v-btn>
              <v-btn v-show="forgotPassword" depressed tile color="primary" @click="sendResetPassword">
                Envoyer
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
import { mdiEye, mdiEyeOff, mdiArrowLeft } from '@mdi/js'

import axios from 'axios'

export default {
  name: 'SignInDdt',
  props: {
    value: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      icons: {
        mdiEye,
        mdiEyeOff,
        mdiArrowLeft
      },
      isLoginValid: false,
      forgotPassword: false,
      sendingRecoveryEmail: false,
      showPassword: false,
      userData: {
        firstname: '',
        lastname: '',
        email: '',
        password: '',
        dept: null,
        isDDT: false
      },
      snackbar: {
        text: '',
        val: false
      },
      error: null
    }
  },
  methods: {
    async signIn () {
      // console.log('signIn', this.$supabase)
      const { user, error } = await this.$auth.signIn(this.userData)

      if (!error) {
        // eslint-disable-next-line no-console
        console.log('success sign in', user)

        if (this.$route.path === '/') {
          this.$router.push('/projets')
        }

        this.$emit('input', false)
      } else {
        this.error = error
      }
    },
    async sendResetPassword () {
      this.forgotPassword = true

      if (!this.isLoginValid) {
        this.$refs.loginForm.validate()
        return
      }

      // this.$supabase.auth.api
      //   .resetPasswordForEmail(this.userData.email, {
      //     redirectTo: window.location.origin
      //   })
      this.sendingRecoveryEmail = true

      await axios({
        method: 'post',
        url: '/api/auth/password',
        data: {
          email: this.userData.email,
          redirectTo: window.location.origin
        }
      })

      this.snackbar.text = `Un email de changement de mot de passe à été envoyé à ${this.userData.email}`
      this.snackbar.val = true

      this.sendingRecoveryEmail = false
      this.forgotPassword = false
    }
  }
}
</script>
