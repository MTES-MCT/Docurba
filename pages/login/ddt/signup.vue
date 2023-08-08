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
  name: 'SignupStateAgent',
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
      showPassword: false,
      userData: {
        firstname: '',
        lastname: '',
        email: '',
        password: '',
        dept: null,
        poste: null,
        region: null,
        isDDT: false
      },
      error: null
    }
  },
  methods: {
    async signUp () {
      try {
        const { user } = await this.$auth.signUpStateAgent({
          ...this.userData,
          dept: this.userData.dept.toString().padStart(2, '0'),
          region: this.userData.region.code.padStart(2, '0')
        })

        axios({
          method: 'post',
          url: '/api/auth/hooksSignupStateAgent',
          data: { ...this.userData, id: user.id }
        })
      } catch (error) {
        console.log(error)
        this.error = error
      }
    }
  }
}
</script>
