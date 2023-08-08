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
                Inscription agent de l'Etat
              </div>
            </v-card-title>
            <validation-observer ref="observerSignupEtat" v-slot="{ handleSubmit }" slim>
              <form @submit.prevent="handleSubmit(signUp)">
                <v-card-text>
                  <v-row justify="center">
                    <v-col cols="12">
                      <OnboardingSignupForm v-model="userData" />
                    </v-col>
                  </v-row>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn class="no-text-transform" outlined tile color="primary" :to="{name: 'login-ddt-signin'}">
                    J'ai déjà un compte
                  </v-btn>
                  <v-btn depressed tile color="primary" @click="signUp()">
                    Créer mon compte
                  </v-btn>
                </v-card-actions>
              </form>
            </validation-observer>
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
import { ValidationObserver } from 'vee-validate'
import axios from 'axios'

export default {
  name: 'LoginDialog',
  components: {
    ValidationObserver
  },
  data () {
    return {
      icons: {
        mdiEye,
        mdiEyeOff,
        mdiArrowLeft
      },
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

    async signUp () {
      try {
        const { user, profile } = await this.$auth.signUp(this.userData)
        await this.$supabase.from('github_ref_roles').insert([{
          role: 'user',
          ref: `dept-${profile.departement}`,
          user_id: user.id
        }])

        this.userData.id = user.id

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
      } catch (error) {
        console.log(error)
        this.error = error
      }
    }
  }
}
</script>
