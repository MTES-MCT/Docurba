<template>
  <div>
    <div
      v-if="visible"
      role="status"
      :class="['login-banner', isFrisePage ? 'login-banner--warning' : 'login-banner--info']"
    >
      <v-icon class="login-banner__icon" size="20">
        {{ isFrisePage ? icons.mdiAlert : icons.mdiInformation }}
      </v-icon>
      <span class="login-banner__text">
        <span v-if="content.bold" class="login-banner__bold">{{ content.bold }}</span>
        <nuxt-link :to="{ name: 'login' }" class="login-banner__link">{{ content.link }}</nuxt-link>
        <template v-if="content.text">{{ content.text }}</template>
      </span>
      <button class="login-banner__close" aria-label="Fermer la bannière" @click="dismiss">
        &times;
      </button>
    </div>
  </div>
</template>

<script>
import { mdiAlert, mdiInformation } from '@mdi/js'
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
      icons: { mdiInformation, mdiAlert }
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

<style scoped>
.login-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  font-size: 16px;
}

.login-banner--info {
  background-color: #E8EDFF;
  color: #0566CC;
}

.login-banner--warning {
  background-color: #FFE9E6;
  color: #B34103;
}

.login-banner__icon {
  color: inherit;
  margin-right: 8px;
}

.login-banner__text {
  text-align: center;
}

.login-banner__bold {
  font-weight: 800;
}

.login-banner__link {
  color: inherit;
  text-decoration: underline;
}

.login-banner__close {
  margin-left: 16px;
  margin-bottom: 2px;
  font-size: 20px;
  cursor: pointer;
  height: 12px;
  display: flex;
  align-items: center;
}
</style>
