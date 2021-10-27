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
        <v-col cols="12" sm="6" md="3" lg="3">
          <v-card flat height="320" color="g100">
            <v-row justify="center">
              <v-col cols="10">
                <v-img height="150px" contain :src="require('@/assets/picto/undraw_search.svg')" />
                <!-- <v-sheet height="200" width="200" color="g300" /> -->
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-card-text>
                  <b>Je précise mon territoire</b> et le type de document d’urbanisme
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3" lg="3">
          <v-card flat height="320" color="g100">
            <v-row justify="center">
              <v-col cols="10">
                <v-img height="150px" contain :src="require('@/assets/picto/undraw_file_analysis.svg')" />
                <!-- <v-sheet height="200" width="200" color="g300" /> -->
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-card-text>
                  <b>J’accède aux premiers éléments</b> fournis par les Services de l’Etat pour mon département
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3" lg="3">
          <v-card flat height="320" color="g100">
            <v-row justify="center">
              <v-col cols="10">
                <v-img height="150px" contain :src="require('@/assets/picto/undraw_profile.svg')" />
                <!-- <v-sheet height="200" width="200" color="g300" /> -->
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-card-text>
                  <b>Je crée un compte</b>
                  et demande mon PAC à ma DDT
                  (Direction Départementale des Territoires)
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3" lg="3">
          <v-card flat height="320" color="g100">
            <v-row justify="center">
              <v-col cols="10">
                <v-img height="150px" contain :src="require('@/assets/picto/undraw_message_sent.svg')" />
                <!-- <v-sheet height="200" width="200" color="g300" /> -->
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-card-text>
                  <b>Je reçois mon PAC en ligne,</b>
                  ma note d’enjeux le cas échéant,
                  et un accompagnement du projet
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
                <v-img contain :src="require('@/assets/picto/undraw_cloud_files.svg')" />
                <!-- <v-sheet color="g300" width="120" height="120" /> -->
              </v-list-item-avatar>

              <v-divider vertical class="rm-divider mr-3 my-2 rm500" />

              <v-list-item-content>
                <v-list-item-title class="text-h3">
                  Direct
                </v-list-item-title>
                <b>Ressources disponibles immédiatement.</b>
                Les documents types et guides, ainsi que les données concernant votre territoire sont mis à votre disposition par les services de l’Etat et téléchargeables aux formats .csv ou .shp.
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-avatar tile size="120">
                <v-img contain :src="require('@/assets/picto/undraw_wireframing.svg')" />
                <v-sheet color="g300" width="120" height="120" />
              </v-list-item-avatar>

              <v-divider vertical class="rm-divider mr-3 my-2 rm500" />

              <v-list-item-content>
                <v-list-item-title class="text-h3">
                  Lisible
                </v-list-item-title>
                <b>Navigation optimisée dans votre porter-à-connaissance.</b>
                Les données et informations du PAC sont mises en forme et faciles à consulter grâce à différents niveaux d’informations, des graphes et des cartes.
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-avatar tile size="120">
                <v-img contain :src="require('@/assets/picto/undraw_collaboration.svg')" />
                <v-sheet color="g300" width="120" height="120" />
              </v-list-item-avatar>

              <v-divider vertical class="rm-divider mr-3 my-2 rm500" />

              <v-list-item-content>
                <v-list-item-title class="text-h3">
                  Collaboratif
                </v-list-item-title>
                <b>Accompagnement des services de l’Etat.</b>
                La plateforme propose une FAQ dédiée, et l’option feuille de route partagée avec la possibilité d’associer des documents aux étapes clés de la procédure. Vous pouvez ainsi offrir de la visibilité aux Services de l’Etat, et aux parties prenantes associées lors de l’élaboration du document d’urbanisme.
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-avatar tile size="120">
                <v-img contain :src="require('@/assets/picto/undraw_done_checking.svg')" />
                <v-sheet color="g300" width="120" height="120" />
              </v-list-item-avatar>

              <v-divider vertical class="rm-divider mr-3 my-2 rm500" />

              <v-list-item-content>
                <v-list-item-title class="text-h3">
                  Complet
                </v-list-item-title>
                <b>Un maximum d’informations centralisées au même endroit.</b>
                Le cadre juridique, les documents supra-territoriaux (SRADDET, SCoT…), les données et le porter à connaissance préparé par la DDT et validé par le préfet disponibles sur une même plateforme.
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
