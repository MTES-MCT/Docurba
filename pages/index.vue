<template>
  <div>
    <!-- START HERO v2 -->
    <v-container fluid>
      <v-row justify="center" align="center" class="primary">
        <v-col cols="auto">
          <a class="white--text" href="https://app.livestorm.co/dinum-12/flash-info-docurba-les-nouveautes-de-loutil?type=detailed" target="_blank"><b>Flash Info de Docurba : jeudi 9 février 2023 à 14h. L'équipe répond à vos questions !</b></a>
        </v-col>
      </v-row>
    </v-container>
    <v-container fluid class="pa-8">
      <v-row class="beige rounded-lg py-16 position-relative">
        <VFloatingShape src="/images/landing/ellipse_half_blue_right.svg" :size="60" :right="15" :bottom="15" />
        <VFloatingShape src="/images/landing/circle_red.svg" :size="54" :left="200" :bottom="-27" />
        <v-col>
          <v-container>
            <v-row>
              <v-col cols="12" class="position-relative">
                <VFloatingShape src="/images/landing/ellipse_blue.svg" :size="70" :left="-15" :top="-20" />
                <VFloatingShape src="/images/landing/ellipse_red.svg" :size="50" :right="100" :top="-20" />
                <VFloatingShape src="/images/landing/circle_yellow.svg" :size="80" :right="200" :bottom="-40" />
                <v-card rounded="lg" class="pa-6">
                  <v-card-title class="">
                    <h2 class="text-h2 black--text break-word">
                      Ressources utiles pour votre <span class="focus--text">document d'urbanisme.</span>
                    </h2>
                  </v-card-title>
                  <v-card-text class="mt-2">
                    <LandingSearchForm />
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            <LandingUserStory />
          </v-container>
        </v-col>
      </v-row>
    </v-container>
    <v-container>
      <LandingDemarche />
      <LandingKeyFeatures class="mt-12" />
    </v-container>
    <v-container>
      <LandingRegionsCard class="mt-12" />
    </v-container>
    <!-- <LandingCtaByNeed /> -->
    <LandingCitations />
    <v-container fluid>
      <v-row class="bf100-g750 mt-16 py-8">
        <LandingNewsLetterForm />
      </v-row>
    </v-container>
  </div>
</template>

<style>
.position-relative {
  position: relative
}

.rm-divider {
  border-width: 0 5px 0 0 !important;
}
</style>
