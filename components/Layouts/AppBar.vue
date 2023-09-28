<template>
  <v-app-bar
    app
    clipped-left
    color="white"
    class="fr-header"
    prominent
  >
    <div class="fr-header__body">
      <div class="fr-container">
        <div class="fr-header__body-row">
          <div class="fr-header__brand fr-enlarge-link">
            <div class="fr-header__brand-top">
              <div class="fr-header__logo">
                <a href="/" title="Accueil - Docurba">
                  <p class="fr-logo">
                    république
                    <br>française
                  </p>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <nuxt-link to="/" title="Accueil - Docurba" class="text-decoration-none g800--text align-self-center ml-10">
      <v-toolbar-title>
        Docurba
        <slot name="pageTitle" />
      </v-toolbar-title>
    </nuxt-link>
    <v-spacer />
    <!-- This client only could be removed with proper user management server side -->
    <client-only>
      <div v-if="!$vuetify.breakpoint.mobile" class="align-self-center">
        <v-btn depressed tile text :to="{name: 'faq'}">
          Besoin d'aide ?
        </v-btn>
        <v-btn v-if="!$user.id" depressed tile text :to="{name: 'login'}">
          Connexion
        </v-btn>
        <v-btn
          v-if="$user.profile.side === 'etat'"
          depressed
          tile
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

        <v-btn v-if="$user.profile.side === 'collectivite'" :to="`/collectivites/${$user.profile.collectivite_id}/?isEpci=${$user.profile.collectivite_id.length > 5}`" depressed tile text>
          Ma collectivité
        </v-btn>
        <v-menu v-if="$user.id" offset-y>
          <template #activator="{ on }">
            <v-btn
              depressed
              tile
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
      </div>
    </client-only>
    <template v-if="extended" #extension>
      <slot />
    </template>
  </v-app-bar>
</template>

<script>
import { mdiDotsVertical } from '@mdi/js'

import '@gouvfr/dsfr/dist/css/header.css'
import '@gouvfr/dsfr/dist/css/logo.css'

export default {
  props: {
    extended: {
      type: Boolean,
      default: false
    }
  },
  data () {
    // console.log(this.$user)

    return {
      icons: {
        mdiDotsVertical
      },
      helpDialog: false,
      helpSnackbar: false
    }
  },
  computed: {
    trameRef () {
      const scopes = { ddt: 'dept', dreal: 'region' }
      const poste = this.$user.profile.poste
      const code = poste === 'ddt' ? this.$user.profile.departement : this.$user.profile.region

      return `${scopes[poste]}-${code}`
    }
  },
  methods: {
    async signOut () {
      await this.$supabase.auth.signOut({ scope: 'global' })
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.fr-header a {
    color: #1e1e1e;
    text-decoration: none;
  }
</style>
