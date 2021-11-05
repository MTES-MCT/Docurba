<template>
  <v-app-bar
    fixed
    app
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
      <!-- <template v-if="!$user.id"> -->
      <v-btn v-if="!$user.id" text @click="openLogin = true">
        Connexion
      </v-btn>
      <LoginDialog v-model="openLogin" />
      <!-- </template> -->
      <!-- <template v-if="$user.id"> -->
      <v-btn v-if="$user.id" text @click="openDocs = true">
        Mes documents
      </v-btn>
      <v-btn v-if="$user.id" text @click="$supabase.auth.signOut()">
        Déconnexion
      </v-btn>
      <DocumentsDialog v-if="$user.id" v-model="openDocs" />
      <!-- </template> -->
    </client-only>
    <template v-if="extended" #extension>
      <slot />
    </template>
  </v-app-bar>
</template>

<script>
export default {
  props: {
    extended: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      openLogin: false,
      openDocs: false
    }
  }
}
</script>
