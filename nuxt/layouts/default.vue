<template>
  <v-app>
    <LayoutsAppBar :flat="$route.name === 'index'" />
    <v-main>
      <nuxt />
    </v-main>
    <LayoutsFooter />
    <VConsentSnackbar />
    <v-snackbar
      v-model="snackbar.val"
      app
      multi-line
      vertical
      :color="snackbar.color"
      :timeout="10000"
    >
      <div>
        {{ snackbar.text }}
      </div>

      <template
        v-if="snackbar.useActionsTemplate"
        #action="{ attrs }"
      >
        <v-btn
          color="white"
          outlined
          class="mr-4"
          tile
          v-bind="attrs"
          :to="{name: 'login-collectivites-signin'}"
        >
          Aller à la page de connexion
        </v-btn>
        <v-btn
          color="white"
          outlined
          tile
          v-bind="attrs"
          @click="snackbar.val = false"
        >
          Fermer
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script>
import axios from 'axios'
import qs from 'qs'

export default {
  name: 'DefaultLayout',
  data () {
    return {
      snackbar: { text: '', val: false, color: '', useActionsTemplate: false }
    }
  },
  async mounted () {
    // TODO: Is not a function  .isReady at init
    if (typeof this.$user.isReady === 'function') {
      await this.$user.isReady.then((resolve, reject) => {
        if (this.$route.path === '/' && this.$user.profile.poste === 'ddt') {
          this.$router.push(`ddt/${this.$user.profile.departement}/collectivites`)
        }
      })
    }

    if (process.browser) {
      const parsed = qs.parse(this.$route.hash.slice(1))
      if (parsed.error) {
        let errorMessage = ''
        if (parsed.error === 'unauthorized_client') {
          errorMessage = 'Le lien de connexion utilisé est expiré. Ce dernier à soit été déjà utilisé, soit est vieux de plus de 1h. Veuillez demander un nouvel envoi de email de  connexion depuis la page de connexion. '
        }
        this.snackbar = {
          val: true,
          text: errorMessage,
          color: 'error',
          useActionsTemplate: true
        }
      }
    }
    // console.log(this.$route.query)
    if (this.$route.query.contact) {
      axios({
        url: '/api/pipedrive/contacted',
        method: 'post',
        data: {
          email: this.$route.query.contact
        }
      })
    }
    const snackbarDict = localStorage.getItem('snackbarDict')
    if (snackbarDict) {
      this.snackbar = { val: true, ...JSON.parse(snackbarDict) }
      localStorage.removeItem('snackbarDict')
    }
  }
}
</script>
