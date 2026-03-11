<template>
  <v-app-bar
    app
    :flat="flat"
    color="white"
    class="app-bar"
    height="94px"
  >
    <div class="app-bar-title">
      <img src="@/assets/images/republique-francaise.svg" class="app-bar-title__logo">
      <img src="@/assets/images/republique-francaise-short.svg" class="app-bar-title__logo--short">

      <nuxt-link to="/" title="Accueil - Docurba" class="app-bar-title__link">
        Docurba
      </nuxt-link>
    </div>

    <div class="app-bar__page-title">
      <slot name="pageTitle" />
    </div>

    <v-spacer />

    <!-- This client only could be removed with proper user management server side -->
    <client-only>
      <div class="app-bar__actions">
        <v-menu v-if="!$user.id" offset-y open-on-hover>
          <template #activator="{ on, attrs }">
            <v-btn
              text
              color="primary"
              class="hidden-xs-only"
              v-bind="attrs"
              v-on="on"
            >
              Solutions
              <v-icon right>
                {{ icons.mdiChevronDown }}
              </v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-subheader class="text-caption text-none">
              Docurba pour:
            </v-subheader>
            <v-list-item :to="'/collectivites-territoriales'">
              <v-list-item-title>Les Collectivités</v-list-item-title>
            </v-list-item>
            <v-list-item :to="'/bureau-etude-urbanisme'">
              <v-list-item-title>Les Bureaux d'Etudes</v-list-item-title>
            </v-list-item>
            <v-list-item :to="'/ddt-ddtm-dreal'">
              <v-list-item-title>Les Services de l'Etat</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
        <v-menu offset-y open-on-hover>
          <template #activator="{ on, attrs }">
            <v-btn
              text
              color="primary"
              class="hidden-xs-only"
              v-bind="attrs"
              v-on="on"
            >
              Documentation
              <v-icon right>
                {{ icons.mdiChevronDown }}
              </v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item link href="https://docurba.crisp.help/fr/category/ressources-1jtg3x2/" target="_blank">
              <v-list-item-title>
                Guide d'utilisation
              </v-list-item-title>
            </v-list-item>
            <v-list-item link href="https://docurba.crisp.help/fr/" target="_blank">
              <v-list-item-title>
                FAQ
              </v-list-item-title>
            </v-list-item>
            <v-list-item link href="https://docurba.crisp.help/fr/category/ressources-1jtg3x2/" target="_blank">
              <v-list-item-title>
                Webinaires
              </v-list-item-title>
            </v-list-item>
            <v-list-item link href="https://docurba.crisp.help/fr/category/nous-contacter-cf4bsp/" target="_blank">
              <v-list-item-title>
                Contact
              </v-list-item-title>
            </v-list-item>
            <v-list-item link to="/dev/api">
              <v-list-item-title>
                API
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>

        <template v-if="$user.id">
          <v-menu offset-y>
            <template #activator="{ on, attrs }">
              <v-btn
                outlined
                color="primary"
                class="no-text-transform"
                v-bind="attrs"
                v-on="on"
              >
                <v-icon
                  left
                  size="20"
                >
                  {{ icons.mdiAccountCircleOutline }}
                </v-icon>
                <span style="line-height: 1;">{{ $user.profile.firstname || 'Mon compte' }}</span>
                <v-icon
                  right
                  size="18"
                >
                  {{ icons.mdiChevronDown }}
                </v-icon>
              </v-btn>
            </template>
            <v-list>
              <v-list-item
                v-if="dashboardRoute"
                :to="dashboardRoute"
              >
                <v-icon
                  size="18"
                  class="mr-3"
                >
                  {{ icons.mdiViewDashboardOutline }}
                </v-icon>
                <v-list-item-title class="text-body-2">
                  {{ dashboardLabel }}
                </v-list-item-title>
              </v-list-item>
              <v-list-item @click="signOut">
                <v-icon
                  size="18"
                  color="error"
                  class="mr-3"
                >
                  {{ icons.mdiLogout }}
                </v-icon>
                <v-list-item-title class="error--text text-body-2">
                  Se déconnecter
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>

          <AuthResetPasswordDialog />
        </template>

        <v-btn
          v-else
          outlined
          color="primary"
          class="no-text-transform"
          :to="{ name: 'login' }"
        >
          <v-icon left>
            {{ icons.mdiAccountCircleOutline }}
          </v-icon>
          Me connecter
        </v-btn>
      </div>
    </client-only>
    <template v-if="extended" #extension>
      <slot />
    </template>
  </v-app-bar>
</template>

<script>
import { mdiChevronDown, mdiAccountCircleOutline, mdiViewDashboardOutline, mdiLogout } from '@mdi/js'

export default {
  props: {
    flat: {
      type: Boolean,
      default: false
    },
    extended: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      icons: {
        mdiChevronDown,
        mdiAccountCircleOutline,
        mdiViewDashboardOutline,
        mdiLogout
      }
    }
  },
  computed: {
    trameRef () {
      const poste = this.$user.profile.poste
      if (!poste) { return null }
      const scopes = { ddt: 'dept', dreal: 'region' }
      const code = poste === 'ddt' ? this.$user.profile.departement : this.$user.profile.region
      if (!code) { return null }

      return `${scopes[poste]}-${this.$options.filters.deptToRef(code)}`
    },
    dashboardRoute () {
      if (!this.$user.id) { return null }
      const { side, poste, departement, collectivite_id: collectiviteId } = this.$user.profile
      if (side === 'ppa') {
        return { name: 'ddt-departement-collectivites', params: { departement } }
      }
      if (side === 'etat') {
        return {
          name: poste === 'ddt' ? 'ddt-departement-collectivites' : 'trames-githubRef',
          params: { departement, githubRef: this.trameRef }
        }
      }
      if (side === 'collectivite') {
        return `/collectivites/${collectiviteId}`
      }
      return null
    },
    dashboardLabel () {
      const { side, poste } = this.$user.profile
      if (side === 'collectivite') { return 'Ma collectivité' }
      if (side === 'etat' && poste !== 'ddt') { return 'Trame régionale' }
      return 'Tableau de bord'
    }
  },
  async mounted () {
    await this.$user.isReady
  },
  methods: {
    async signOut () {
      const { error } = await this.$supabase.auth.signOut()
      if (error) {
        return console.error('signOut error:', error)
      }
      this.$router.push('/')
    }
  }
}
</script>

<style>
.app-bar .v-toolbar__content {
  padding: 8px 40px;
}

.app-bar-title {
  width: auto !important;
  display: flex;
  align-items: center;
  gap: 2.5rem;
}

.app-bar-title__logo--short {
  display: none;
}

.app-bar-title__link {
  font-size: 28px;
  font-weight: 700;
  text-decoration: none;
  color: var(--v-g800-base) !important;
}

.app-bar__page-title {
  font-size: 20px;
  margin-left: 16px;
}

.app-bar__actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.app-bar__actions .v-btn__content {
  text-transform: none !important;
}

@media screen and (max-width: 960px) {
  .app-bar-title {
    gap: 1rem;
  }

  .app-bar-title__logo {
    display: none;
  }

  .app-bar-title__logo--short {
    display: block;
  }

  .app-bar-title__link {
    font-size: 20px;
  }

  .app-bar .v-toolbar__content {
    padding: 8px 16px;
  }
}
</style>
