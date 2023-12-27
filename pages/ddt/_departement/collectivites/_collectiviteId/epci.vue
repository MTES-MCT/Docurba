<template>
  <v-container v-if="collectivite">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          {{ collectivite.intitule }}
        </h1>
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <nuxt-link

            :to="{ name: 'ddt-departement-collectivites', params: { departement: $route.params.departement }}"
          >
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span>Revenir à mon tableau de bord</span>
          </nuxt-link>
        </div>
      </v-col>
      <v-col cols="12">
        <v-expansion-panels flat>
          <v-expansion-panel class="border-light">
            <v-expansion-panel-header>
              <h3>{{ collectivite.communes?.length }} communes dans votre EPCI</h3>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-container>
                <v-row>
                  <v-col
                    v-for="town in collectivite.communes"
                    :key="town.code"
                    cols="4"
                    class="pt-0 pl-0"
                  >
                    <nuxt-link :to="{ name: 'ddt-departement-collectivites-collectiviteId-commune', params: { departement: $route.params.departement, collectiviteId: town.code }}">
                      {{ town.intitule }} ({{ town.code }})
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
    <template v-if="loaded">
      <v-row>
        <v-col cols="12">
          <v-alert type="info">
            Date du dernier extract de données Sudocuh vers Docurba: <b>13 Décembre 2023</b>
          </v-alert>
        </v-col>
        <v-col cols="12">
          <p class="text-h2">
            Documents d'urbanisme
          </p>
          <p class="text-h6">
            Documents d’urbanisme sous la compétence de {{ collectivite.intitule }} :
          </p>
        </v-col>
      </v-row>
      <DashboardDUItemsList
        collectivite-type="epci"
        :collectivite="collectivite"
        :procedures="plans"
        :projects="projects"
        :schemas="schemas"
        @deleteProcedure="getProcedures"
      />
    </template>
    <v-row v-else>
      <v-col cols="12">
        <VGlobalLoader />
      </v-col>
    </v-row>
  </v-container>
  <v-container v-else>
    <v-row>
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
      loaded: false,
      collectivite: null,
      projects: [],
      plans: [],
      schemas: [],
      icons: {
        mdiArrowLeft
      }
    }
  },
  async mounted () {
    await this.getProcedures()
    this.loaded = true
  },
  methods: {
    async getProcedures () {
      this.collectivite = (await axios({ url: `/api/geo/collectivites/${this.$route.params.collectiviteId}` })).data
      const { plans, schemas } = await this.$urbanisator.getProjects(this.$route.params.collectiviteId)
      this.schemas = schemas
      this.plans = plans
      console.log('schemas: ', schemas, ' plans: ', plans)
      console.log('this.collectivite: ', this.collectivite.communes.map(e => e.type))
    }
  }
}
</script>
