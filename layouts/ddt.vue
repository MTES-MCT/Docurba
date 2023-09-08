<template>
  <v-app>
    <LayoutsAppBarDdt />
    <v-main class="beige">
      <v-container v-if="isLoading" class="fill-height">
        <v-row justify="center" align="center">
          <v-col cols="12">
            <VGlobalLoader />
          </v-col>
        </v-row>
      </v-container>
      <template v-else>
        <nuxt v-if="isAllowed" keep-alive />
        <v-container v-else class="fill-height">
          <v-row justify="center" align="center">
            <v-col cols="12" class="mb-4">
              <div class="text-center text-h2">
                En attente de validation
              </div>
            </v-col>
            <v-col cols="12">
              <v-img height="200" contain src="/images/errors/maintenance.svg" />
            </v-col>
          </v-row>
        </v-container>
      </template>
    </v-main>
    <LayoutsFooter />
  </v-app>
</template>

<script>
// import '@gouvfr/dsfr/dist/css/core.css'
import '@gouvfr/dsfr/dist/css/footer.css'
import '@gouvfr/dsfr/dist/css/logo.css'

import axios from 'axios'

export default {
  name: 'DdtLayout',
  computed: {
    isLoading () {
      return !this.$user.profile.email
    },
    isAllowed () {
      console.log('this.$user?.profile: ', this.$user.profile)
      return this.$user?.profile?.side === 'etat' && this.$user?.profile?.verified
    }
  },
  async mounted () {
    await this.$user.isReady
    if (this.$user.profile.side !== 'etat') { this.$router.push('/') }

    if (this.$route.query.contact) {
      axios({
        url: '/api/pipedrive/contacted',
        method: 'post',
        data: {
          email: this.$route.query.contact
        }
      })
    }
  }
}
</script>

<style scoped>
  .v-footer.footer-fr {
    border-top: 2px #000091 solid !important;
    /* border-top-color: var(--v-bf500); */
  }

  .footer-fr ul {
    list-style: none;
  }

  .footer-fr a {
    color: #1e1e1e;
    text-decoration: none;
  }
</style>
