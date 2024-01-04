<template>
  <div>
    <v-container>
      <v-row class="beige rounded-lg py-md-16 position-relative mt-md-4">
        <VFloatingShape class=" d-none d-md-flex" src="/images/landing/ellipse_half_blue_right.svg" :size="60" :right="15" :bottom="15" />
        <VFloatingShape class=" d-none d-md-flex" src="/images/landing/circle_red.svg" :size="54" :left="200" :bottom="-27" />
        <v-col cols="12">
          <v-container>
            <v-row>
              <v-col cols="12" class="position-relative">
                <VFloatingShape src="/images/landing/ellipse_blue.svg" :size="70" :left="-15" :top="-20" />
                <VFloatingShape src="/images/landing/ellipse_red.svg" :size="50" :right="100" :top="-20" />
                <VFloatingShape src="/images/landing/circle_yellow.svg" :size="80" :right="200" :bottom="-40" />
                <v-card rounded="lg" class="pa-6" style="z-index:1">
                  <v-card-title class="">
                    <h2 class="text-h2 black--text break-word">
                      Ressources utiles autour de votre <span class="focus--text">document d'urbanisme.</span>
                    </h2>
                  </v-card-title>
                  <v-card-text class="mt-2">
                    <LandingSearchForm />
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-container>
          <client-only>
            <LandingUserStory :id="!$vuetify.breakpoint.mobile ? 'container-user-stories' : ''" />
          </client-only>
        </v-col>
      </v-row>
    </v-container>
    <v-container>
      <v-row>
        <v-col cols="12" class="mt-16">
          <div class="primary lighten-3 my-12 pa-8">
            <p class="font-weight-bold">
              Vous êtes agent de l'Etat et voulez paramétrer votre trame de PAC et suivre les procédures de votre département ?
            </p>
            <div>
              <v-btn depressed color="primary" class="mr-6" to="/login/ddt/signup" nuxt>
                S'inscrire
              </v-btn>
              <v-btn class="custom-transform-class text-none" outlined color="primary" to="/login/ddt/signin" nuxt>
                Se connecter
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
      <LandingDemarche class="mb-12" />
      <LandingKeyFeatures class="mt-12" />
    </v-container>
    <LandingCitations />
    <v-container fluid>
      <v-row class="bf100-g750 mt-16 py-8">
        <LandingNewsLetterForm />
      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  name: 'Landing',
  data () {
    return {}
  }
}

</script>
<style>
.position-relative {
  position: relative
}

.rm-divider {
  border-width: 0 5px 0 0 !important;
}

#container-user-stories{
  position:absolute;
  bottom:-28%;
  left:0
}
</style>
