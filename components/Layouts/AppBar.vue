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
              Ressources
              <v-icon right>
                {{ icons.mdiChevronDown }}
              </v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item link href="https://pad.numerique.gouv.fr/s/lzpwuS7N0#%F0%9F%93%96-Nos-Guides-d%E2%80%99utilisation" target="_blank">
              <v-list-item-title>
                Guide d'utilisation
              </v-list-item-title>
            </v-list-item>
            <v-list-item link :to="{name: 'faq'}">
              <v-list-item-title>
                FAQ
              </v-list-item-title>
            </v-list-item>
            <v-list-item link href="https://pad.numerique.gouv.fr/s/lzpwuS7N0#%F0%9F%93%BA-Nos-webinaires-et-formations-en-ligne" target="_blank">
              <v-list-item-title>
                Webinaires
              </v-list-item-title>
            </v-list-item>
            <v-list-item link :to="{name: 'faq', query: { action: 'Nous contacter', scope: 1 } }">
              <v-list-item-title>
                Contact
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>

        <template v-if="$user.id">
          <v-btn
            v-if="$user.profile.side === 'etat'"
            depressed
            color="primary"
            :to="{
              name: $user.profile.poste === 'ddt' ? 'ddt-departement-collectivites' : 'trames-githubRef',
              params: {
                departement: $user.profile.departement,
                githubRef: trameRef
              }
            }"
          >
            {{ $user.profile.poste === 'ddt' ? 'Tableau de bord' : 'Trame regionale' }}
          </v-btn>
          <v-btn
            v-else-if="$user.profile.side === 'collectivite'"
            depressed
            color="primary"
            :to="`/collectivites/${$user.profile.collectivite_id}`"
          >
            Ma collectivité
          </v-btn>

          <v-menu offset-y>
            <template #activator="{ on }">
              <v-btn
                depressed
                icon
                small
                v-on="on"
              >
                <v-icon>{{ icons.mdiDotsVertical }}</v-icon>
              </v-btn>
            </template>
            <v-list>
              <v-list-item link @click="signOut">
                <v-list-item-title>
                  Déconnexion
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>

          <AuthResetPasswordDialog />
        </template>

        <v-btn v-else depressed color="primary" :to="{ name: 'login' }">
          Connexion
        </v-btn>
      </div>
    </client-only>
    <template v-if="extended" #extension>
      <slot />
    </template>
  </v-app-bar>
</template>

<script>
import { mdiDotsVertical, mdiChevronDown } from '@mdi/js'

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
        mdiDotsVertical,
        mdiChevronDown
      }
    }
  },
  computed: {
    trameRef () {
      const scopes = { ddt: 'dept', dreal: 'region' }
      const poste = this.$user.profile.poste
      const code = poste === 'ddt' ? this.$user.profile.departement : this.$user.profile.region

      return `${scopes[poste]}-${this.$options.filters.deptToRef(code)}`
    }
  },
  async mounted () {
    await this.$user.isReady
  },
  methods: {
    async signOut () {
      await this.$supabase.auth.signOut()
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
