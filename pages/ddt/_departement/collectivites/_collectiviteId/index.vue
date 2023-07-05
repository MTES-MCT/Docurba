<template>
  <v-container v-if="collectivite">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          {{ collectivite.name }} <span v-if="collectivite.code_commune_INSEE">({{ collectivite.code_commune_INSEE }})</span>
        </h1>
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <div style="cursor:pointer;" class="d-flex align-center primary--text text-decoration-underline" @click="back">
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span v-if="$store.getters.routeIsEpci">Revenir à mon tableau de bord</span>
            <span v-else>Revenir à l'EPCI</span>
          </div>
          <div class="ml-8">
            <span v-if="linkedEpci" class="text-h5">Appartient à {{ linkedEpci.label }}</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12">
        <v-expansion-panels v-if="$store.getters.routeIsEpci" flat>
          <v-expansion-panel class="border-light">
            <v-expansion-panel-header>
              <h3>{{ collectivite.towns?.length }} communes dans votre EPCI</h3>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-container>
                <v-row>
                  <v-col
                    v-for="town in collectivite.towns"
                    :key="town.code_commune_INSEE"
                    cols="4"
                    class="pt-0 pl-0"
                  >
                    <nuxt-link :to="{ name: 'ddt-departement-collectivites-collectiviteId', params: { departement: $route.params.departement, collectiviteId: town.code_commune_INSEE }, query: { isEpci: false } }">
                      {{ town.nom_commune }} ({{ town.code_commune_INSEE }})
                    </nuxt-link>
                    <v-divider class="mt-3" />
                  </v-col>
                </v-row>
              </v-container>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <p class="text-h2">
          Documents d'urbanisme
        </p>
        <p class="text-h6">
          Documents d’urbanisme disponibles pour la commune recherchée :
        </p>
      </v-col>
    </v-row>
    <v-row v-if="procedures && procedures.length > 0">
      <v-col v-if="!$store.getters.routeIsEpci" cols="12">
        <DashboardDUItem
          v-for="(procedure,i) in procedures"
          :key="'du_' + i"
          :procedure="procedure"
        />
      </v-col>
      <v-col v-else>
        <v-tabs
          v-model="tab"
          background-color="primary"
          dark
        >
          <v-tab>
            DU intercommunaux
          </v-tab>
          <v-tab>
            DU communaux
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="tab" class="beige">
          <v-tab-item>
            <DashboardDUItem
              v-for="(procedure,i) in DUInter"
              :key="'du_' + i"
              :procedure="procedure"
            />
          </v-tab-item>
          <v-tab-item>
            <DashboardDUItem
              v-for="(procedure,i) in DUCommunaux"
              :key="'du_' + i"
              :procedure="procedure"
            />
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
    <v-row v-else-if="procedures && procedures.length === 0">
      <v-col cols="12">
        <div class="text--secondary beige pa-6 mb-12 rounded">
          Cette collectivité n'a pas de documents d'urbanisme sous ca compétence.
        </div>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12">
        <VGlobalLoader />
      </v-col>
    </v-row>
  </v-container>
</template>
<script>

import { mdiArrowLeft } from '@mdi/js'
import axios from 'axios'

export default {
  name: 'Collectivite',
  layout: 'ddt',
  data () {
    return {
      linkedEpci: null,
      tab: null,
      collectivite: null,
      procedures: null,
      icons: {
        mdiArrowLeft
      }
    }
  },
  computed: {
    DUCommunaux () {
      return this.procedures?.filter(e => e.perimetre.length === 1)
    },
    DUInter () {
      return this.procedures?.filter(e => e.perimetre.length > 1)
    }
  },

  async mounted () {
    this.collectivite = await this.$sudocu.getCurrentCollectivite(this.$route.params.collectiviteId)
    this.procedures = await this.$sudocu.getProcedures(this.collectivite)
    if (!this.$store.getters.routeIsEpci) {
      await this.getLinkedEpci(this.$route.params.collectiviteId)
    }
  },
  methods: {
    back () {
      console.log('BACK: ', this.$store.getters.routeIsEpci, ' !this.linkedEpci: ', !this.linkedEpci)
      if (this.$store.getters.routeIsEpci || !this.linkedEpci) {
        console.log('BACK TO LIST')
        this.$router.push({ name: 'ddt-departement-collectivites', params: { departement: this.$route.params.departement } })
      } else {
        this.$router.push({ name: 'ddt-departement-collectivites-collectiviteId', params: { departement: this.$route.params.departement, collectiviteId: this.linkedEpci.EPCI }, query: { isEpci: true } })
      }
    },
    async getLinkedEpci (communeId) {
      const { data: epci } = await axios({
        url: `/api/epci?communeId=${communeId}`,
        method: 'get'
      })
      this.linkedEpci = epci[0]
    }
  }
}
</script>

<style lang="scss">
.border-light{
  border: solid 1px var(--v-primary-lighten1) !important;
}
</style>
