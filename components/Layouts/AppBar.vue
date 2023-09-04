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
      <div class="align-self-center">
        <v-btn depressed tile text :to="{name: 'faq'}">
          Besoin d'aide ?
        </v-btn>
        <v-btn v-if="!$user.id" depressed tile text :to="{name: 'login'}">
          Connexion
        </v-btn>
        <!-- <AuthLoginDialog v-model="openLogin" /> -->
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
          Tableau de bord
        </v-btn>
        <v-btn v-if="$user.profile.side === 'etat'" depressed tile text @click="clickMyDocs">
          Mes documents
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
            <v-list-item v-if="$user.profile.side === 'etat'" link @click="goToAdmin">
              <v-list-item-title>Accès DDT/DEAL</v-list-item-title>
            </v-list-item>
            <v-list-item link @click="signOut">
              <v-list-item-title>
                Déconnexion
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
        <!-- <v-btn depressed tile v-if="$user.id" text @click="$supabase.auth.signOut()">
        Déconnexion
      </v-btn> -->
        <DocumentsDialog v-if="$user.id" v-model="openDocs" />
        <AdminDdtRequestDialog v-model="openDDT" />
        <AuthResetPasswordDialog />
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
      helpSnackbar: false,
      openLogin: false,
      openDocs: false,
      openDDT: false,
      adminAccess: null
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
    // There is a lot of dupliaceted code here.
    // This component should be using the auth.js plugin to get admin access.
    async getAdminAccess () {
      if (!this.adminAccess) {
        const { data: adminAccess } = await this.$supabase.from('admin_users_dept').select('role').match({
          user_id: this.$user.id,
          user_email: this.$user.email,
          role: 'ddt'
        })

        this.adminAccess = adminAccess
      }

      return this.adminAccess
    },
    async goToAdmin () {
      const { data: adminAccess } = await this.$supabase.from('admin_users_dept').select('role').match({
        user_id: this.$user.id,
        user_email: this.$user.email,
        role: 'ddt'
      })

      if (adminAccess && adminAccess.length) {
        this.$router.push('/projets')
      } else {
        this.openDDT = true
      }
    },
    async clickMyDocs () {
      await this.getAdminAccess()

      if (this.adminAccess) {
        this.$router.push('/projets')
      } else {
        this.openDocs = true
      }
    },
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
</style>
