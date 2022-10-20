<template>
  <div>
    <!-- START HERO v2 -->
    <v-container fluid class="pa-8">
      <v-row class="beige rounded-lg py-16">
        <v-col>
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-card rounded="lg" class="pa-6">
                  <v-card-title class="">
                    <h2 class="text-h2 black--text">
                      Ressources utiles pour votre <span class="focus--text">document d'urbanisme.</span>
                    </h2>
                  </v-card-title>
                  <v-card-text class="mt-2">
                    <v-row justify="center" align="center">
                      <v-col cols="2">
                        <v-select
                          v-model="searchQuery.document"
                          filled
                          hide-details
                          dense
                          placeholder="Type de document"
                          :items="documents"
                        />
                      </v-col>
                      <v-col v-if="searchQuery.document && searchQuery.document.includes('i')" cols="">
                        <VEpciAutocomplete v-model="selectedEpci" />
                      </v-col>
                      <v-col v-else cols="">
                        <VTownAutocomplete v-model="selectedTown" :cols-dep="4" :cols-town="8" />
                      </v-col>
                      <v-col cols="auto">
                        <v-btn
                          depressed
                          color="primary"
                          :loading="searchLoading"
                          @click="searchCTA"
                        >
                          <v-icon class="mr-2" small>
                            {{ icons.mdiMagnify }}
                          </v-icon>
                          Rechercher
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            <LandingUserStory />
          </v-container>
        </v-col>
      </v-row>
    </v-container>
    <!-- END HERO v2 -->
    <!-- <v-container fluid class="g100 pb-16">
      <v-row justify="center" align="center" class="pt-16">
        <v-col cols="12" sm="10" md="10">
          <h1 class="text-h1 text-center">
            Docurba centralise les ressources utiles pour élaborer votre document d'urbanisme
          </h1>
        </v-col>
        <v-col cols="12" sm="8" md="8">
          <p class="text-center">
            Docurba, la plateforme mise en place par les services de l’Etat pour les collectivités et leurs bureaux d’étude afin de faciliter l'élaboration des documents d'urbanisme et la prise en compte des informations et enjeux environnementaux
          </p>
        </v-col>
      </v-row>
      <v-row justify="center" align="center">
        <v-col cols="2">
          <v-select
            v-model="searchQuery.document"
            filled
            hide-details
            placeholder="Type de document"
            :items="documents"
          />
        </v-col>
        <v-col v-if="searchQuery.document && searchQuery.document.includes('i')" cols="8" sm="6">
          <VEpciAutocomplete v-model="selectedEpci" />
        </v-col>
        <v-col v-else cols="8" sm="6">
          <VTownAutocomplete v-model="selectedTown" :cols-dep="4" :cols-town="8" />
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-col cols="auto">
          <v-btn
            depressed
            tile
            color="primary"
            x-large
            :loading="searchLoading"
            @click="searchCTA"
          >
            Rechercher
          </v-btn>
        </v-col>
      </v-row>
    </v-container> -->
    <v-container>
      <!-- User stories -->
      <v-row class="py-16">
        <v-col cols="12">
          <h2 class="text-h2">
            Comment ça marche?
          </h2>
        </v-col>
      </v-row>
    </v-container>
    <LandingUserStory />
    <LandingCitations />
    <!-- <LandingCtaByNeed /> -->
    <LandingKeyFeatures />
    <v-row class="g100 mt-16 py-16">
      <LandingNewsLetterForm />
    </v-row>
  </div>
</template>

<script>
import axios from 'axios'
import { mdiMagnify } from '@mdi/js'
import regions from '@/assets/data/Regions.json'

export default {
  data () {
    return {
      documents: ['CC', 'PLU', 'PLUi', 'PLUi-H', 'PLUi-D', 'PLUi-HD'], // 'SCoT', 'SCot-AEC'],
      searchQuery: {
        region: null,
        document: null
      },
      selectedEpci: null,
      selectedTown: null,
      searchLoading: false,
      icons: {
        mdiMagnify
      }
    }
  },
  computed: {
    searchLink () {
      const query = {
        insee: [this.selectedTown ? this.selectedTown.code_commune_INSEE : '']
      }

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
  },
  watch: {
    selectedTown () {
      this.searchQuery.region = regions.find(r => r.name === this.selectedTown.nom_region)
    }
  },
  methods: {
    async searchCTA () {
      if (this.searchQuery.document && this.searchQuery.document.includes('i')) {
        this.searchLoading = true

        const EPCI = (await axios({
          method: 'get',
          url: `/api/epci/${this.selectedEpci.id}`
        })).data

        const regionCode = EPCI.towns[0].code_region
        // eslint-disable-next-line eqeqeq
        const region = regions.find(r => r.code == regionCode)

        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Recherche',
          `${region.iso} - ${this.selectedEpci.label}`
        ])

        this.$router.push({
          path: '/pacsec/content',
          query: Object.assign({}, this.searchLink.query, {
            insee: EPCI.towns.map(t => t.code_commune_INSEE),
            region: region.iso
          })
        })

        this.searchLoading = false
      } else {
        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Recherche',
          `${this.selectedTown.code_departement} - ${this.selectedTown.nom_commune}`
        ])

        this.$router.push(this.searchLink)
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
