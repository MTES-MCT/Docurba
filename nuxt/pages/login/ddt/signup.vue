<template>
  <v-container class="fill-height">
    <v-row>
      <v-col cols="12">
        <div>
          <v-alert v-if="error" type="error">
            Une erreur s'est produite. Vérifiez que cette adresse email n'est pas déjà associée à un compte ou essayez de nouveau dans quelques minutes.
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
            <v-alert v-if="disabled" dense text type="info" class="ma-4">
              Les créations de compte sont temporairement indisponibles. En nous excusant pour la gêne occasionnée, merci de bien vouloir nous écrire à <a href="mailto:contact@docurba.beta.gouv.fr?subject=Inscription" target="_blank" rel="noopener noreferrer">contact@docurba.beta.gouv.fr</a> : nous pourrons ainsi vous informer lors du rétablissement du service.
            </v-alert>
            <validation-observer ref="observerSignupEtat" v-slot="{ handleSubmit }">
              <form @submit.prevent="handleSubmit(signUp)">
                <v-card-text>
                  <v-row justify="center">
                    <v-col cols="12">
                      <OnboardingSignupForm
                        v-model="userData"
                        :disabled="disabled"
                      />
                    </v-col>
                  </v-row>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn class="no-text-transform" outlined tile color="primary" :to="{name: 'login-ddt-signin'}">
                    J'ai déjà un compte
                  </v-btn>
                  <v-btn
                    depressed
                    tile
                    color="primary"
                    :loading="loading"
                    type="submit"
                    :disabled="disabled"
                  >
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
        region: null,
        optin: false
      },
      error: false,
      disabled: true
    }
  },
  methods: {
    async signUp () {
      this.error = false
      this.loading = true

      try {
        await this.$nuxtApi.post('/api/auth/signupStateAgent', {
          userData: {
            ...this.userData,
            departement: this.userData.departement?.code_departement.toString().padStart(2, '0'),
            region: this.userData.region?.code.padStart(2, '0') || this.userData.departement?.code_region.toString().padStart(2, '0')
          }
        })
        this.$router.push({ name: 'login-ddt-explain' })
      } catch (error) {
        this.error = true
        this.$vuetify.goTo(0)
      }

      this.loading = false
    }
  }
}
</script>
