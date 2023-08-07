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
                Recevoir mon lien de connexion d'accès Collectivité
              </div>
            </v-card-title>
            <v-card-text>
              <v-row justify="center">
                <v-col cols="12">
                  <v-text-field v-model="email" hide-details filled label="Email" />
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn outlined tile color="primary" :to="{name: 'login-collectivites-signup'}">
                Pas de compte ? Créez en un
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
import { mdiArrowLeft } from '@mdi/js'
import axios from 'axios'

export default {
  name: 'SigninCollectivite',
  data () {
    return {
      icons: {
        mdiArrowLeft
      },
      email: '',
      snackbar: {
        text: '',
        val: false
      },
      error: null
    }
  },
  methods: {
    async signInCollectivite () {
      try {
        const ret = await axios({
          method: 'post',
          url: '/api/auth/signinCollectivite',
          data: {
            email: this.email
          }
        })
        console.log('ret: ', ret)
        this.$router.push({ name: 'login-collectivites-explain' })
      } catch (error) {
        this.error = error.response.data.message
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
