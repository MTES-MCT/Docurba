<template>
  <v-footer app absolute color="white pt-12">
    <v-container fluid :style="{ maxWidth: '1160px' }" class="pa-0">
      <v-row>
        <v-col cols="12" md="6">
          <h5>Ressources</h5>
          <ul :style="{ listStyle: 'none' }" class="pa-0 mt-4">
            <li>
              <a href="https://pad.incubateur.net/s/MVwW7cGNh#Nos-Guides-d%E2%80%99utilisation" _target="blank">Guides d'utilisation</a>
            </li>
            <li>
              <a href="https://docurba.beta.gouv.fr/faq">FAQ</a>
            </li>
            <li>
              <a href="https://pad.incubateur.net/s/MVwW7cGNh#Nos-webinaires">Webinaires</a>
            </li>
            <li>
              <nuxt-link to="/accessibilite">
                Accessibilité: non conforme
              </nuxt-link>
            </li>
            <li>
              <nuxt-link to="/confidentialite">
                Politique de confidentialité
              </nuxt-link>
            </li>
            <li>
              <nuxt-link to="/mentions-legales">
                Mentions légales
              </nuxt-link>
            </li>
            <li>
              <nuxt-link to="/stats">
                Statistiques
              </nuxt-link>
            </li>
          </ul>
        </v-col>
        <v-col cols="12" md="6">
          <v-row>
            <v-col>
              <h5>Newsletter</h5>
              <p class="mt-4">
                Suivez l’avancée de Docurba tous les mois.
              </p>
              <LandingNewsLetterForm />
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <h5>Réseaux sociaux</h5>
              <div class="mt-4 d-flex" :style="{ gap: '1rem' }">
                <a href="https://www.linkedin.com/company/docurba/" target="_blank">
                  <v-img max-width="40px" height="40px" :src="require('@/assets/images/icons/linkedin.svg')" />
                </a>
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<style scoped>
h5 {
  font-size: 22px;
}

a {
  text-decoration: none;
  color: inherit;
}
</style>
