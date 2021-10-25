<template>
  <div>
    <v-container fluid>
      <!-- Hero -->
      <v-row justify="center" align="center" class="pt-16 g100">
        <v-col cols="12" sm="10" md="10">
          <h1 class="text-h1 text-center">
            Docurba : démarrez et suivez l’élaboration de votre document d’urbanisme dans les meilleures conditions
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
    <v-container>
      <!-- User stories -->
      <v-row class="py-16">
        <v-col cols="12">
          <h2 class="text-h2">
            Comment ça marche?
          </h2>
        </v-col>
      </v-row>
      <v-row justify="space-around" align="center">
        <v-col cols="12" sm="5" md="4" lg="3">
          <v-card flat height="340" color="g100">
            <v-row justify="center">
              <v-col cols="10">
                <v-img :src="require('@/assets/picto/undraw_data_processing.svg')" />
                <!-- <v-sheet height="200" width="200" color="g300" /> -->
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-card-text>
                  J’accède à des ressources et données territorialisées pour bien démarrer mon projet de document d’urbanisme
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
        <v-col cols="12" sm="5" md="4" lg="3">
          <v-card flat height="340" color="g100">
            <v-row justify="center">
              <v-col cols="10">
                <v-img :src="require('@/assets/picto/undraw_reviewed_docs.svg')" />
                <!-- <v-sheet height="200" width="200" color="g300" /> -->
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-card-text>
                  J’accède aux éléments d’information du porter à connaissance concernant mon territoire
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
        <v-col cols="12" sm="5" md="4" lg="3">
          <v-card flat height="340" color="g100">
            <v-row justify="center">
              <v-col cols="10">
                <v-img :src="require('@/assets/picto/undraw_progress_indicator.svg')" />
                <!-- <v-sheet height="200" width="200" color="g300" /> -->
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-card-text>
                  Je bénéficie de l'accompagnement de l’Etat : cadre partenarial, porter à connaissance réglementaire en ligne, note d’enjeux le cas échéant, échanges
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>

      <!-- Eléments de différenciation -->
      <v-row class="mt-16" justify="center" align="center">
        <v-col cols="12" sm="12" md="12">
          <h2 class="text-h2">
            Les atouts de Docurba
          </h2>
        </v-col>
        <v-col cols="12" sm="12" md="12">
          <v-list>
            <v-list-item>
              <v-list-item-avatar tile size="120">
                <v-img :src="require('@/assets/picto/undraw_cloud_files.svg')" />
                <!-- <v-sheet color="g300" width="120" height="120" /> -->
              </v-list-item-avatar>

              <v-divider vertical class="rm-divider mr-3 my-2 rm500" />

              <v-list-item-content>
                <v-list-item-title class="text-h3">
                  Direct
                </v-list-item-title>
                <b>Ressources et informations disponibles et téléchargeables immédiatement.</b>
                Les documents types et guides, ainsi que les données et informations concernant votre territoire sont mis à votre disposition par les services de l’Etat pour bien démarrer votre projet.
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-avatar tile size="120">
                <v-img :src="require('@/assets/picto/undraw_wireframing.svg')" />
                <v-sheet color="g300" width="120" height="120" />
              </v-list-item-avatar>

              <v-divider vertical class="rm-divider mr-3 my-2 rm500" />

              <v-list-item-content>
                <v-list-item-title class="text-h3">
                  Digeste
                </v-list-item-title>
                <b>Navigation optimisée pour les éléments d’informations de votre porter à connaissance.</b>
                Les données et informations du PAC sont triées et mises en forme pour vous simplifier l’appropriation du contenu. Différents niveaux d’informations, graphes et cartes sont proposés dans la navigation.
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-avatar tile size="120">
                <v-img :src="require('@/assets/picto/undraw_collaboration.svg')" />
                <v-sheet color="g300" width="120" height="120" />
              </v-list-item-avatar>

              <v-divider vertical class="rm-divider mr-3 my-2 rm500" />

              <v-list-item-content>
                <v-list-item-title class="text-h3">
                  Collaboratif
                </v-list-item-title>
                <b>Accompagnement des services de l’Etat.</b>
                Un cadre partenarial permet de choisir le niveau de relation souhaité pour être soutenu dans la réalisation de votre document d’urbanisme. Un espace d’échange est ouvert aux questions.
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-col>
      </v-row>
    </v-container>
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
