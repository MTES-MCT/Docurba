<template>
  <v-dialog v-model="dialog" width="700">
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
            <v-col v-if="error && error.status === 400" cols="12">
              <span class="error--text">Email ou mot de passe incorrecte.</span>
            </v-col>
            <v-spacer />
            <v-col cols="auto">
              <v-btn depressed tile text small @click="sendResetPassword">
                Mot de passe oublié ?
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
        <v-btn depressed tile color="primary" @click="loginTemplate === 'Inscription' ? signUp() : signIn()">
          {{ loginTemplate }}
        </v-btn>
        <v-btn depressed tile color="primary" outlined @click="toggleTemplate">
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

import axios from 'axios'

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
        password: '',
        dept: null,
        isDDT: false
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

      if (!error) {
        // eslint-disable-next-line no-console
        console.log('success sign in', user, session)

        if (this.$route.path === '/') {
          this.$router.push('/projets')
        }

        this.$emit('input', false)
      } else {
        this.error = error
      }
    },
    async signUp () {
      const {
        // user,
        // session,
        error
      } = await this.$auth.signUp(this.userData)

      if (!error) {
        // eslint-disable-next-line no-console
        // console.log('success sign up', user, session)

        if (this.userData.isDDT && this.userData.dept) {
          await this.$supabase.from('admin_users_dept').insert([{
            role: 'user',
            dept: this.userData.dept.code_departement,
            user_id: this.$user.id,
            user_email: this.$user.email
          }])

          axios({
            url: '/api/slack/notify/admin',
            method: 'post',
            data: {
              userData: this.userData
            }
          })
        }

        axios({
          method: 'post',
          url: '/api/auth/signup',
          data: {
            email: this.userData.email,
            userData: this.userData,
            redirectTo: window.location.origin
          }
        })

        this.$emit('input', false)
      } else {
        this.error = error
      }
    },
    sendResetPassword () {
      // this.$supabase.auth.api
      //   .resetPasswordForEmail(this.userData.email, {
      //     redirectTo: window.location.origin
      //   })

      axios({
        method: 'post',
        url: '/api/auth/password',
        data: {
          email: this.userData.email,
          redirectTo: window.location.origin
        }
      })

      this.snackbar.text = `Un email de changement de mot de passe à été envoyé à ${this.userData.email}`
      this.snackbar.val = true
    }
  }
}
</script>
