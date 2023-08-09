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
        <v-btn v-if="$user?.profile?.poste === 'ddt'" depressed tile text :to="{name: 'ddt-departement-collectivites', params: {departement: $user.profile.departement}}">
          Tableau de bord
        </v-btn>
        <v-btn v-if="$user.id" depressed tile text @click="clickMyDocs">
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
            <v-list-item link @click="goToAdmin">
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
    <template #extension>
      <v-tabs align-with-title class="double-border">
        <v-tab :to="{name: 'ddt-departement-collectivites', params: {departement: $user?.profile?.departement}}">
          Mes collectivites
        </v-tab>
        <v-tab
          :to="{name: 'trames-githubRef', params: {githubRef: `dept-${$user?.profile?.departement}`} }"
        >
          Trame de PAC départementale
        </v-tab>
        <v-tab
          :to="
            {name:
               'ddt-departement-collectivites-enquete',
             params:
               {departement:
                 $user?.profile?.departement}}"
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
      },
      openLogin: false,
      openDocs: false,
      openDDT: false,
      adminAccess: null
    }
  },
  async mounted () {
    await this.$user.isReady
    console.log('this.$user: ', this.$user)
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

.fr-header .double-border{
  border-top: solid 1px var(--v-grey-base);
  border-bottom: solid 1px var(--v-grey-base);
}

.fr-header .v-tab{
  color: var(--v-typo-base) !important;
  text-transform: none;
}

</style>
