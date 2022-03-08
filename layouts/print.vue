<template>
  <v-app class="print-container">
    <v-app-bar
      app
      elevation="0"
      color="white"
      class="fr-header"
      height="68px"
      fixed
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
    </v-app-bar>
    <v-main>
      <nuxt />
    </v-main>
  </v-app>
</template>

<script>
import '@gouvfr/dsfr/dist/css/header.css'
import '@gouvfr/dsfr/dist/css/logo.css'
export default {

}
</script>

<style scoped>
@page {
  margin: 0mm;
}

.fr-header {
  padding: 17mm;
}

.fr-header .v-toolbar__content {
  padding: 0mm;
}

.fr-header .fr-header__body-row, .fr-header .fr-header__logo, .fr-header .fr-logo {
  padding: 0mm !important;
  margin: 0mm !important
}

.fr-header a {
  color: #1e1e1e;
  text-decoration: none;
}

.print-container {
  padding: 17mm;
}
</style>
