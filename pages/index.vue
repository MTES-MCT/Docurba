<template>
  <div>
    <v-container fluid>
      <!-- Hero -->
      <v-row justify="center" align="center" class="pt-16 g100">
        <v-col cols="12" sm="10" md="10">
          <h1 class="text-h1 text-center">
            Docurba, la plateforme qui centralise les ressources utiles pour élaborer votre document d’urbanisme
          </h1>
        </v-col>
        <v-col cols="12" sm="8" md="8">
          <p class="text-center">
            Docurba, la plateforme mise en place par les services de l’Etat pour les collectivités et leurs bureaux d’étude afin de faciliter l'élaboration des documents d'urbanisme et la prise en compte des informations et enjeux environnementaux
          </p>
        </v-col>
      </v-row>
      <v-row class="pb-16 g100" justify="center" align="center">
        <v-col cols="auto">
          <!-- <v-btn color="primary">
          Rechercher
        </v-btn> -->
          <v-select
            v-model="searchQuery.document"
            filled
            hide-details
            placeholder="Type de document"
            :items="documents"
          />
        </v-col>
        <v-col cols="3">
          <VRegionAutocomplete v-model="searchQuery.region" />
        </v-col>
        <v-col cols="auto">
          <v-btn color="primary" x-large nuxt :to="searchLink">
            Rechercher
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
    <LandingCtaByNeed />
    <LandingUserStory />
    <LandingKeyFeatures />
  </div>
</template>

<script>

export default {
  data () {
    return {
      documents: ['CC', 'PLU', 'PLUi', 'PLUi-H', 'PLUi-D', 'PLUi-HD', 'SCoT', 'SCot-AEC'],
      searchQuery: {
        region: null,
        document: null
      }
    }
  },
  computed: {
    searchLink () {
      const query = {}

      if (this.searchQuery.region) {
        query.region = this.searchQuery.region.iso
      }

      if (this.searchQuery.document) {
        query.document = this.searchQuery.document
      }

      return {
        path: '/pacsec/content',
        query
      }
    }
  }
}
</script>

<style>
.rm-divider {
  border-width: 0 5px 0 0 !important;
}
</style>
