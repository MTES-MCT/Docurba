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
          <div class="d-flex align-center primary--text text-decoration-underline" @click="$router.back()">
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span v-if="isEpci">Revenir à mon tableau de bord</span>
            <span v-else>Revenir à l'EPCI</span>
          </div>
          <div class="ml-8">
            <span v-if="!isEpci" class="text-h5">Nom de l'EPCI lié</span>
          </div>
        </div>
      </v-col>
      <v-col cols="12">
        <v-expansion-panels v-if="isEpci" flat>
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
                    <nuxt-link :to="{ name: 'dashboard-departement-collectivites-collectiviteId', params: { departement: $route.params.departement, collectiviteId: town.code_commune_INSEE }, query: { isEpci: false } }">
                      {{ town.nom_commune }}
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
          Documents d’urbanismes disponibles pour la commune recherchée :
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
import SudocuEvents from '@/mixins/SudocuEvents.js'

export default {
  mixins: [SudocuEvents],
  data () {
    return {
      icons: {
        mdiArrowLeft
      }
    }
  }
}
</script>
