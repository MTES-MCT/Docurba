<template>
  <v-app>
    <LayoutsAppBar />
    <v-main :class="$route.name.startsWith('login') ? 'beige' : ''">
      <nuxt />
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
  name: 'DefaultLayout',
  mounted () {
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
