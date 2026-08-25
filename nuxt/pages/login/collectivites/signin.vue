<template>
  <v-container class="fill-height">
    <v-row>
      <v-col cols="12">
        <v-alert
          v-if="error"
          type="error"
        >
          {{ error }}
        </v-alert>
        <div class="mb-2">
          <nuxt-link :to="{ name: 'login' }">
            <v-icon
              class="mr-2"
              color="primary"
              small
            >
              {{ icons.mdiArrowLeft }}
            </v-icon>
            Retour
          </nuxt-link>
        </div>
        <v-card
          class="border-light"
          flat
        >
          <validation-observer
            ref="observerSignIn"
            v-slot="{ handleSubmit }"
          >
            <form @submit.prevent="handleSubmit(submit)">
              <v-card-title>
                <div class="text-h1">
                  {{ label }}
                </div>
              </v-card-title>
              <v-card-text>
                <validation-provider
                  v-slot="{ errors }"
                  name="Email"
                  rules="required|email"
                >
                  <v-text-field
                    v-model="email"
                    :error-messages="errors"
                    filled
                    label="Email"
                  />
                </validation-provider>
                <InputsPasswordTextField
                  v-if="isSignInWithPassword"
                  v-model="password"
                />
                <v-row
                  v-if="!isPasswordReset"
                  justify="end"
                >
                  <v-col cols="auto">
                    <v-btn
                      v-if="isSignInWithPassword"
                      color="primary"
                      text
                      @click="isPasswordReset = true"
                    >
                      Mot de passe oublié ? Cliquez ici
                    </v-btn>
                    <v-btn
                      v-else
                      color="primary"
                      text
                      @click="isSignInWithPassword = true"
                    >
                      Se connecter avec un mot de passe
                    </v-btn>
                  </v-col>
                </v-row>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn
                  v-if="isPasswordReset"
                  color="primary"
                  outlined
                  title
                  @click="isPasswordReset = false"
                >
                  Retour
                </v-btn>
                <v-btn
                  v-else-if="isSignInWithPassword"
                  color="primary"
                  outlined
                  title
                  @click="isSignInWithPassword = false"
                >
                  Se connecter avec un lien
                </v-btn>
                <v-btn
                  v-else
                  color="primary"
                  outlined
                  title
                  :to="{ name: 'login-collectivites-signup' }"
                >
                  Pas de compte ? Créez en un
                </v-btn>
                <v-btn
                  color="primary"
                  depressed
                  title
                  type="submit"
                >
                  {{ submitLabel }}
                </v-btn>
              </v-card-actions>
            </form>
          </validation-observer>
        </v-card>
        <v-snackbar
          v-model="isSnackbarVisible"
          app
          :timeout="4000"
        >
          {{ snackbar }}
        </v-snackbar>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mdiArrowLeft } from '@mdi/js'
import axios from 'axios'
import FormInput from '@/mixins/FormInput'

const MODE = {
  LINK: 'link',
  PASSWORD: 'password',
  RESET: 'reset'
}

export default {
  name: 'SignInCollectivite',
  mixins: [FormInput],
  data () {
    return {
      email: '',
      error: null,
      icons: { mdiArrowLeft },
      mode: MODE.LINK,
      password: '',
      snackbar: ''
    }
  },
  computed: {
    isPasswordReset: {
      get () {
        return this.mode === MODE.RESET
      },
      set (value) {
        this.mode = value ? MODE.RESET : MODE.PASSWORD
      }
    },
    isSignInWithPassword: {
      get () {
        return this.mode === MODE.PASSWORD
      },
      set (value) {
        this.mode = value ? MODE.PASSWORD : MODE.LINK
      }
    },
    isSnackbarVisible: {
      get () {
        return !!this.snackbar
      },
      set (value) {
        if (!value && !!this.snackbar) {
          this.snackbar = ''
        }
      }
    },
    label () {
      return this.isPasswordReset
        ? 'Réinitialisation de mot de passe'
        : 'Connexion collectivité'
    },
    submitLabel () {
      switch (this.mode) {
        case MODE.PASSWORD:
          return 'Se connecter'
        case MODE.RESET:
          return 'Recevoir mon lien de réinitialisation'
        default:
          return 'Recevoir mon lien de connexion'
      }
    }
  },
  methods: {
    async sendResetPasswordLink () {
      try {
        await axios({
          method: 'post',
          url: '/api/auth/password',
          data: {
            email: this.email,
            redirectTo: window.location.origin
          }
        })

        this.snackbar = `Un email de changement de mot de passe à été envoyé à ${this.email}`
      } catch (error) {
        this.error = error.response.data.message
      }

      this.isPasswordReset = false
    },
    async sendSignInLink () {
      try {
        await axios({
          method: 'post',
          url: '/api/auth/signinCollectivite',
          data: {
            email: this.email,
            redirectTo: window.location.origin
          }
        })

        this.snackbar = `Un email de connexion à été envoyé à ${this.email}. Cliquez sur le lien dans l'email pour être connecté automatiquement.`
      } catch (error) {
        this.error = error.response.data.message
      }
    },
    async signIn () {
      try {
        const { error } = await this.$auth.signIn({
          email: this.email,
          password: this.password
        })

        if (error) {
          throw error
        }
      } catch (error) {
        this.error = 'Email ou mot de passe incorrect.'
      }
    },
    submit () {
      switch (this.mode) {
        case MODE.PASSWORD:
          return this.signIn()
        case MODE.RESET:
          return this.sendResetPasswordLink()
        default:
          return this.sendSignInLink()
      }
    }
  }
}
</script>
