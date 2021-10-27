<template>
  <v-app>
    <v-app-bar
      fixed
      app
      color="white"
    >
      <nuxt-link to="/" class="text-decoration-none g800--text">
        <v-toolbar-title>
          Docurba
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
        <DocumentsDialog v-if="$user.id" v-model="openDocs" @created="navToProject" />
        <!-- </template> -->
      </client-only>
    </v-app-bar>
    <v-main>
      <nuxt />
    </v-main>
    <v-footer class="footer-fr" color="white">
      <v-row align="center" class="mt-4 ml-1">
        <v-col cols="12" md="5">
          <div class="fr-footer__brand">
            <a class="fr-logo" href="/" title="république française">
              <span class="fr-logo__title">république
                <br>française</span>
            </a>
            <a class="fr-footer__brand-link" href="https://beta.gouv.fr/">
              <img class="fr-footer__logo" src="https://d33wubrfki0l68.cloudfront.net/8a59b7696f7c0a39fa0904ddac1769a772e249e5/a88f5/assets/additional/images/logo-betagouvfr.svg" alt="gouv.fr">
            </a>
          </div>
        </v-col>
        <v-col cols="12" md="3">
          <div class="text-caption">
            Docurba est un projet d'innovation pour faciliter l’élaboration des documents d’urbanisme en prenant en compte les informations et enjeux environnementaux.
          </div>
        </v-col>
        <v-col cols="12" md="4">
          <div class="fr-footer__content">
            <ul class="fr-footer__content-list">
              <li class="fr-footer__content-item">
                <a class="fr-footer__content-link" href="https://legifrance.gouv.fr">legifrance.gouv.fr</a>
              </li>
              <li class="fr-footer__content-item">
                <a class="fr-footer__content-link" href="https://gouvernement.fr">gouvernement.fr</a>
              </li>
              <li class="fr-footer__content-item">
                <a class="fr-footer__content-link" href="https://service-public.fr">service-public.fr</a>
              </li>
              <li class="fr-footer__content-item">
                <a class="fr-footer__content-link" href="https://data.gouv.fr">data.gouv.fr</a>
              </li>
            </ul>
          </div>
        </v-col>
      </v-row>
    </v-footer>
  </v-app>
</template>

<script>
// import '@gouvfr/dsfr/dist/css/core.css'
import '@gouvfr/dsfr/dist/css/footer.css'
import '@gouvfr/dsfr/dist/css/logo.css'

export default {
  data () {
    return {
      openLogin: false,
      openDocs: false
    }
  },
  methods: {
    navToProject (project) {
      this.openDocs = false
      this.$router.push(`/projets/${project.id}`)
    }
  }
}
</script>

<style scoped>
  .v-footer.footer-fr {
    border-top: 2px #000091 solid !important;
    /* border-top-color: var(--v-bf500); */
  }

  .footer-fr ul {
    list-style: none;
  }

  .footer-fr a {
    color: #1e1e1e;
    text-decoration: none;
  }
</style>
