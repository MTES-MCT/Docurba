<template>
  <v-dialog v-model="dialog" width="400">
    <v-card>
      <v-card-title>
        Connexion
      </v-card-title>
      <!-- SIGNIN -->
      <template v-if="loginTemplate === 'Connexion'">
        <v-card-text>
          <v-row justify="end">
            <v-col cols="12">
              <v-text-field v-model="userData.email" hide-details filled label="Email" />
            </v-col>
            <v-col cols="12">
              <InputsPasswordTextField v-model="userData.password" />
            </v-col>
            <v-spacer />
            <v-col cols="auto">
              <v-btn text small @click="sendResetPassword">
                Mot de passe oublier ?
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </template>
      <!-- SIGNUP -->
      <template v-if="loginTemplate === 'Inscription'">
        <v-card-text>
          <v-row justify="center">
            <v-col cols="12">
              <OnboardingSignupForm v-model="userData" />
            </v-col>
          </v-row>
        </v-card-text>
      </template>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="loginTemplate === 'Inscription' ? signUp() : signIn()">
          {{ loginTemplate }}
        </v-btn>
        <v-btn color="primary" outlined @click="toggleTemplate">
          {{ loginTemplate === 'Inscription' ? 'Connexion' : 'Inscription' }}
        </v-btn>
      </v-card-actions>
    </v-card>
    <v-snackbar
      v-model="snackbar.val"
      :timeout="4000"
    >
      {{ snackbar.text }}
    </v-snackbar>
  </v-dialog>
</template>

<script>
import { mdiEye, mdiEyeOff } from '@mdi/js'

export default {
  name: 'LoginDialog',
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
        mdiEyeOff
      },
      showPassword: false,
      userData: {
        firstname: '',
        lastname: '',
        email: '',
        password: ''
      },
      snackbar: {
        text: '',
        val: false
      },
      loginTemplate: 'Connexion',
      error: null
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
    toggleTemplate () {
      this.loginTemplate = [
        'Connexion',
        'Inscription'
      ].find(d => d !== this.loginTemplate)
    },
    async signIn () {
      // console.log('signIn', this.$supabase)
      const { user, session, error } = await this.$auth.signIn(this.userData)

      console.log('login', user, session, error)

      if (!error) {
        // eslint-disable-next-line no-console
        console.log('success sign in', user, session)

        this.$emit('input', false)
      } else {
        this.error = error
      }
    },
    async signUp () {
      const { user, session, error } = await this.$auth.signUp(this.userData)

      if (!error) {
        // eslint-disable-next-line no-console
        console.log('success sign up', user, session)

        this.$emit('input', false)
      } else {
        this.error = error
      }
    },
    sendResetPassword () {
      this.$supabase.auth.api
        .resetPasswordForEmail(this.userData.email, {
          redirectTo: window.location.origin
        })

      this.snackbar.text = `Un email de changement de mot de passe à été envoyé à ${this.userData.email}`
      this.snackbar.val = true
    }
  }
}
</script>
