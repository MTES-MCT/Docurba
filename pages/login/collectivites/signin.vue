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
            <validation-observer ref="observerSignInCollectivite" v-slot="{ handleSubmit }">
              <form @submit.prevent="handleSubmit(signInCollectivite)">
                <v-card-title>
                  <div class="text-h1">
                    Recevoir mon lien de connexion d'accès Collectivité
                  </div>
                </v-card-title>
                <v-card-text>
                  <v-row justify="center">
                    <v-col cols="12">
                      <validation-provider v-slot="{ errors }" name="E-mail" rules="required|email">
                        <v-text-field v-model="email" :error-messages="errors" filled label="Email" />
                      </validation-provider>
                    </v-col>
                  </v-row>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn outlined tile color="primary" :to="{name: 'login-collectivites-signup'}">
                    Pas de compte ? Créez en un
                  </v-btn>
                  <v-btn depressed tile color="primary" type="submit">
                    Recevoir mon lien de connexion par email
                  </v-btn>
                </v-card-actions>
              </form>
            </validation-observer>
          </v-card>
        </div>
      </v-col>
    </v-row>
    <v-snackbar
      v-model="snackbar.val"
      :timeout="4000"
    >
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script>
import { mdiArrowLeft } from '@mdi/js'
import axios from 'axios'
import FormInput from '@/mixins/FormInput.js'

export default {
  name: 'SignInCollectivite',
  mixins: [FormInput],
  data () {
    return {
      icons: { mdiArrowLeft },
      snackbar: { text: '', val: false },
      email: '',
      error: null
    }
  },
  methods: {
    async signInCollectivite () {
      try {
        await axios({
          method: 'post',
          url: '/api/auth/signinCollectivite',
          data: {
            email: this.email,
            redirectTo: window.location.origin
          }
        })
        this.snackbar = {
          val: true,
          text: `Un email de connexion à été envoyé à ${this.email}. Cliquez sur le lien dans le mail pour être connecté automatiquement.`
        }
        // this.$router.push({ name: 'login-collectivites-explain' })
      } catch (error) {
        this.error = error.response.data.message
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
