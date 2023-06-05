<template>
  <v-container v-if="collectivite">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          {{ collectivite.name }}
        </h1>
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <div style="cursor:pointer;" class="d-flex align-center primary--text text-decoration-underline" @click="back">
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span v-if="routeIsEpci">Revenir à mon tableau de bord</span>
            <span v-else>Revenir à l'EPCI</span>
          </div>
          <div class="ml-8">
            <span v-if="linkedEpci" class="text-h5">Appartient à {{ linkedEpci.label }}</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12">
        <v-expansion-panels v-if="routeIsEpci" flat>
          <v-expansion-panel class="beige">
            <v-expansion-panel-header>
              <h3>{{ collectivite.towns.length }} communes dans votre EPCI</h3>
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
      <v-col cols="12">
        <DashboardDUItem
          v-for="(procedure,i) in procedures"
          :key="'du_' + i"
          :procedure="procedure"
        />
      </v-col>
    </v-row>
  </v-container>
</template>
<script>

import { mdiArrowLeft } from '@mdi/js'
import axios from 'axios'
import SudocuEvents from '@/mixins/SudocuEvents.js'

export default {
  mixins: [SudocuEvents],
  data () {
    return {
      linkedEpci: null,
      icons: {
        mdiArrowLeft
      }
    }
  },
  async mounted () {
    if (!this.routeIsEpci) {
      await this.getLinkedEpci(this.$route.params.collectiviteId)
    }
    // this.$route.params.collectiviteId.toString().padStart(5, '0')
    // .eq('towns->>code_commune_INSEE', 30140)
    // .contains('towns', [{ code_commune_INSEE: 30140 }])
    // const { data: test, error } = await this.$supabase.from('projects').select('*').contains('towns', JSON.stringify([{ code_commune_INSEE: 73001 }]))
    // console.log('TEST LASALLE: ', test)
    // if (error) {
    //   console.log('TEST error: ', error)
    // }
  },
  methods: {
    back () {
      if (this.routeIsEpci || !this.linkedEpci) {
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
      console.log('EPCI LINKED: ', epci)
    }
  }
}
</script>
