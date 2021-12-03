<template>
  <v-app-bar
    app
    clipped-left
    color="white"
  >
    <nuxt-link to="/" class="text-decoration-none g800--text">
      <v-toolbar-title>
        Docurba
        <slot name="pageTitle" />
      </v-toolbar-title>
    </nuxt-link>
    <v-spacer />
    <!-- This client only could be removed with proper user management server side -->
    <client-only>
      <v-btn v-if="!$user.id" text @click="openLogin = true">
        Connexion
      </v-btn>
      <LoginDialog v-model="openLogin" />
      <v-btn v-if="$user.id" text @click="openDocs = true">
        Mes documents
      </v-btn>
      <v-menu v-if="$user.id" offset-y>
        <template #activator="{ on }">
          <v-btn
            icon
            small
            v-on="on"
          >
            <v-icon>{{ icons.mdiDotsVertical }}</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item link @click="openDDT = true">
            <v-list-item-title>Accès DDT</v-list-item-title>
          </v-list-item>
          <v-list-item link @click="$supabase.auth.signOut()">
            <v-list-item-title>
              Déconnexion
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
      <!-- <v-btn v-if="$user.id" text @click="$supabase.auth.signOut()">
        Déconnexion
      </v-btn> -->
      <DocumentsDialog v-if="$user.id" v-model="openDocs" />
      <AdminDdtRequestDialog v-model="openDDT" />
    </client-only>
    <template v-if="extended" #extension>
      <slot />
    </template>
  </v-app-bar>
</template>

<script>
import { mdiDotsVertical } from '@mdi/js'

export default {
  props: {
    extended: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      icons: {
        mdiDotsVertical
      },
      openLogin: false,
      openDocs: false,
      openDDT: false
    }
  }
}
</script>
