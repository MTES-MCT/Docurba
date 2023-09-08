<template>
  <v-app-bar
    app
    flat
    clipped-left
    color="white"
    height="78"
    class="fr-header"
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
      <div class="align-self-center">
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
          text
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
        <AuthResetPasswordDialog />
      </div>
    </client-only>
    <template #extension>
      <v-tabs v-if="$user.profile.verified" align-with-title class="double-border">
        <v-tab
          v-if="$user.profile.poste === 'ddt'"
          :to="{
            name: 'ddt-departement-collectivites',
            params: {departement: $user.profile.departement}
          }"
        >
          Mes collectivites
        </v-tab>
        <v-tab
          :to="{
            name: 'trames-githubRef',
            params: {githubRef: trameRef}
          }"
        >
          Trame de PAC {{ trameRef.includes('region') ? 'regionale' : 'départementale' }}
        </v-tab>
        <v-tab
          :to="{
            name:'ddt-departement-collectivites-enquete',
            params: {departement: $user.profile.departement}
          }"
        >
          Validation des procédures
        </v-tab>
      </v-tabs>
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
      }
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
  async mounted () {
    await this.$user.isReady
    // console.log('this.$user: ', this.$user)
  },
  methods: {
    signOut () {
      this.$supabase.auth.signOut()
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

.fr-header .double-border{
  border-top: solid 1px var(--v-grey-base);
  border-bottom: solid 1px var(--v-grey-base);
}

.fr-header .v-tab{
  color: var(--v-typo-base) !important;
  text-transform: none;
}

</style>
