<template>
  <v-dialog v-model="dialog" width="500">
    <v-card>
      <v-card-title>
        Connexion
      </v-card-title>
      <!-- SIGNIN -->
      <template v-if="loginTemplate === 'Connexion'">
        <v-card-text>
          <v-row justify="center">
            <v-col cols="12" md="8">
              <v-text-field v-model="userData.email" filled label="Email" />
            </v-col>
          </v-row>
          <v-row justify="center">
            <v-col cols="12" md="8">
              <v-text-field
                v-model="userData.password"
                filled
                label="Mot de passe"
                :type="showPassword ? 'text' : 'password'"
                :append-icon="showPassword ? icons.mdiEye : icons.mdiEyeOff"
                @click:append="showPassword = !showPassword"
              />
            </v-col>
          </v-row>
          <v-row justify="center">
            <v-col cols="auto">
              <v-btn color="primary" @click="signIn">
                Connexion
              </v-btn>
            </v-col>
          </v-row>
          <v-row justify="center">
            <v-col cols="auto">
              <v-btn color="primary" outlined @click="toggleTemplate">
                Inscription
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </template>
      <!-- SIGNUP -->
      <template v-if="loginTemplate === 'Inscription'">
        <v-card-text>
          <v-row justify="center">
            <v-col cols="12" md="8">
              <v-text-field v-model="userData.email" filled label="Email" />
            </v-col>
          </v-row>
          <v-row justify="center">
            <v-col cols="12" md="8">
              <v-text-field
                v-model="userData.password"
                filled
                label="Mot de passe"
                :type="showPassword ? 'text' : 'password'"
                :append-icon="showPassword ? icons.mdiEye : icons.mdiEyeOff"
                @click:append="showPassword = !showPassword"
              />
            </v-col>
          </v-row>
          <v-row justify="center">
            <v-col cols="12" md="8">
              <v-text-field v-model="userData.firstname" filled label="Prénom" />
            </v-col>
          </v-row>
          <v-row justify="center">
            <v-col cols="12" md="8">
              <v-text-field v-model="userData.lastname" filled label="Nom" />
            </v-col>
          </v-row>
          <v-row justify="center">
            <v-col cols="auto">
              <v-btn color="primary" @click="signUp">
                Inscription
              </v-btn>
            </v-col>
          </v-row>
          <v-row justify="center">
            <v-col cols="auto">
              <v-btn color="primary" outlined @click="toggleTemplate">
                Connexion
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </template>
    </v-card>
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
      const { user, session, error } = await this.$supabase.auth.signIn({
        email: this.userData.email,
        password: this.userData.password
      })

      if (!error) {
        // eslint-disable-next-line no-console
        console.log('success sign in', user, session)

        this.$emit('input', false)
      } else {
        this.error = error
      }
    },
    async signUp () {
      const { user, session, error } = await this.$supabase.auth.signUp({
        email: this.userData.email,
        password: this.userData.password
      }, {
        data: {
          firstname: this.userData.firstname,
          lastname: this.userData.lastname
        }
      })

      if (!error) {
        // eslint-disable-next-line no-console
        console.log('success sign up', user, session)

        this.$emit('input', false)
      } else {
        this.error = error
      }
    }
  }
}
</script>
