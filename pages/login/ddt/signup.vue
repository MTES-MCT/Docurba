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
          <v-card flat class="border-light">
            <v-card-title>
              <div class="text-h1">
                Inscription agent de l'Etat
              </div>
            </v-card-title>
            <validation-observer ref="observerSignupEtat" v-slot="{ handleSubmit }">
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
                  <!-- @click="signUp()" -->
                  <v-btn depressed tile color="primary" :loading="loading" type="submit">
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
import { omit } from 'lodash'

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
      loading: false,
      userData: {
        firstname: '',
        lastname: '',
        email: '',
        password: '',
        departement: null,
        poste: null,
        region: null
      },
      error: null
    }
  },
  methods: {
    async signUp () {
      try {
        this.loading = true
        await this.$auth.signUpStateAgent({
          ...this.userData,
          departement: this.userData.departement?.code_departement.toString().padStart(2, '0'),
          region: this.userData.region?.code.padStart(2, '0')
        })

        const sanitizedUserData = omit(this.userData, ['password'])
        axios({
          method: 'post',
          url: '/api/auth/hooksSignupStateAgent',
          data: sanitizedUserData
        })
        this.$router.push({ name: 'login-ddt-explain' })
      } catch (error) {
        this.error = error.message
        this.$vuetify.goTo(0)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
