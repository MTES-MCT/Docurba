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
          <v-card>
            <v-card-title>
              <div class="text-h1">
                Recevoir mon lien de connexion d'accès Collectivité
              </div>
            </v-card-title>
            <v-card-text>
              <v-row justify="center">
                <v-col cols="12">
                  <v-text-field v-model="userData.email" hide-details filled label="Email" />
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn text tile color="primary" :to="{name: 'login-collectivites-signup'}">
                Pas de compte ? Créer en un
              </v-btn>
              <v-btn depressed tile color="primary" @click="signInCollectivite">
                Recevoir mon lien de connexion par email
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
  name: 'LoginDialog',
  data () {
    return {
      icons: {
        mdiEye,
        mdiEyeOff,
        mdiArrowLeft
      },
      roles: [
        { text: 'Bureau d\'étude', value: 'BE' },
        { text: 'Maire', value: 'Commune' },
        { text: 'EPCI', value: 'EPCI' }
      ],
      isLoginValid: false,
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

    async signInCollectivite () {
      const {
        // user,
        // session,
        error
      } = await this.$auth.signUp(this.userData)

      if (!error) {
        // eslint-disable-next-line no-console
        // console.log('success sign up', user, session)

        if (this.userData.isDDT && this.userData.dept) {
          const { data: { session: { user } } } = await this.$supabase.auth.getSession()

          await this.$supabase.from('github_ref_roles').insert([{
            role: 'user',
            ref: `dept-${this.userData.dept.code_departement}`,
            user_id: user.id
          }])

          this.userData.id = user.id
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
    }
  }
}
</script>
