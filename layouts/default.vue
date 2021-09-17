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
    </v-app-bar>
    <v-main>
      <nuxt />
    </v-main>
    <v-footer class="d-none footer-fr">
      <v-row justify="center">
        <!-- <v-col cols="6">
          <div class="fr-footer__brand fr-enlarge-link">
            <a href="/" title="Retour à l’accueil">
              <p class="fr-logo">
                république
                <br>française
              </p>
            </a>
          </div>
        </v-col> -->
        <v-col cols="auto">
          Docurba est un projet d'innovation pour faciliter l’élaboration des documents d’urbanisme en prenant en compte les informations et enjeux environnementaux.
        </v-col>
      </v-row>
    </v-footer>
  </v-app>
</template>

<script>
// import '@gouvfr/dsfr/dist/css/footer.css'

export default {
}
</script>

<style scoped>
  .footer-fr {
    border-top: 2px black solid;
    border-top-color: var(--v-bf500);
  }
</style>
