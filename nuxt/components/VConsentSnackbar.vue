<template>
  <v-snackbar
    v-model="opened"
    app
    light
    :timeout="-1"
    bottom
    left
  >
    <b>Nous utilisons des cookies dans notre stratégie de déploiement.
      Vous pouvez en apprendre plus <nuxt-link to="/confidentialite">
        ici
      </nuxt-link>.</b>
    <template #action>
      <v-btn color="primary" class="mr-2" tile @click="setConsent('true')">
        Accepter
      </v-btn>
      <v-btn color="primary" depressed outlined tile @click="setConsent('false')">
        Refuser
      </v-btn>
    </template>
  </v-snackbar>
</template>
<script>
const cookieConsentValue = '12-12-2024'

export default {
  data () {
    return {
      opened: false
    }
  },
  mounted () {
    this.readConsent()
  },
  methods: {
    setConsent (val) {
      localStorage.setItem('cookie-consent', `${cookieConsentValue}-${val}`)
      this.readConsent()
    },
    readConsent () {
      const consent = localStorage.getItem('cookie-consent')

      if (!consent) {
        this.opened = true
      } else {
        this.opened = false
        if (consent === `${cookieConsentValue}-true` && !process.dev) {
          this.$gtag()
        }
      }
    }
  }
}
</script>
