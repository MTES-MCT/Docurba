<template>
  <div>
    <div
      v-if="visible"
      role="status"
      :class="['d-flex align-center justify-center py-3 px-4 text-body-2', isFrisePage ? 'warning-bg warning-text--text' : 'bf200 primary--text text--lighten-2']"
    >
      <v-icon class="mr-2" style="color: inherit" size="20">
        {{ isFrisePage ? icons.mdiAlert : icons.mdiInformation }}
      </v-icon>
      <span class="text-center">
        <span v-if="content.bold" class="font-weight-bold">{{ content.bold }}</span>
        <nuxt-link :to="{ name: 'login' }" style="color: inherit; text-decoration: underline;">{{ content.link }}</nuxt-link>
        <template v-if="content.text">{{ content.text }}</template>
      </span>
      <v-btn
        icon
        small
        class="ml-4"
        aria-label="Fermer la bannière"
        color="inherit"
        @click="dismiss"
      >
        <v-icon size="18" class="mt-1">
          {{ icons.mdiClose }}
        </v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script>
import { mdiAlert, mdiInformation, mdiClose } from '@mdi/js'
const SESSION_KEY = 'login-banner-dismissed'
const BANNER_CONTENT = {
  frise: {
    bold: 'Vous êtes actuellement en mode public, la visibilité des informations est limitée.',
    text: ' Vous représentez un territoire ou l\'État ?',
    link: 'Identifiez-vous'
  },
  default: {
    bold: 'Vous représentez un territoire ou l\'État ?',
    link: 'Identifiez-vous',
    text: ' pour accéder à plus d\'informations et suivre vos documents d\'urbanisme'
  }
}

export default {
  name: 'LoginBanner',
  data () {
    return {
      dismissed: false,
      ready: false,
      icons: { mdiInformation, mdiAlert, mdiClose }
    }
  },
  computed: {
    visible () {
      return this.ready && !this.dismissed && !this.isLoginPage && !this.$user.id
    },
    isFrisePage () {
      return this.$route.name && this.$route.name.startsWith('frise')
    },
    isLoginPage () {
      return this.$route.name && this.$route.name.startsWith('login')
    },
    content () {
      return this.isFrisePage ? BANNER_CONTENT.frise : BANNER_CONTENT.default
    }
  },
  mounted () {
    this.dismissed = sessionStorage.getItem(SESSION_KEY) === 'true'
    this.ready = true
  },
  methods: {
    dismiss () {
      this.dismissed = true
      sessionStorage.setItem(SESSION_KEY, 'true')
    }
  }
}
</script>
