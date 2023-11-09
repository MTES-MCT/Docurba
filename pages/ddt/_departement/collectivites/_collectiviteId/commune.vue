<template>
  <v-container v-if="collectivite && procedures">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          {{ collectivite.intitule }} ({{ collectivite.code }})
        </h1>
      </v-col>
      <v-col cols="12">
        <div v-if="collectivite.intercommunaliteCode" class="d-flex">
          <nuxt-link :to="{ name: 'ddt-departement-collectivites-collectiviteId-epci', params: { departement: collectivite.intercommunalite.departementCode, collectiviteId: collectivite.intercommunaliteCode }}">
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span>Revenir à l'EPCI</span>
          </nuxt-link>
          <div class="ml-8">
            <span class="text-h5">Appartient à {{ collectivite.intercommunalite.intitule }}</span>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-alert type="info">
          Date du dernier extract de données Sudocuh vers Docurba: <b>4 Octobre 2023</b>
        </v-alert>
      </v-col>
      <v-col cols="12">
        <p class="text-h2">
          Documents d'urbanisme
        </p>
        <p class="text-h6">
          Documents d’urbanisme disponibles pour la commune recherchée :
        </p>
      </v-col>
    </v-row>
    <DashboardDUItemsList
      :collectivite="collectivite"
      :procedures="procedures"
      :projects="projects"
      :schemas="schemas"
      @inserted="fetchProjects"
    />
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
      procedures: [],
      sudocuProcedures: [],
      projects: [],
      schemas: [],
      icons: {
        mdiArrowLeft
      }
    }
  },
  async mounted () {
    const { collectivite, schemas, procedures: sudocuProcedures } = (await axios({ url: `/api/urba/collectivites/${this.$route.params.collectiviteId}`, method: 'get' })).data
    this.collectivite = collectivite
    this.schemas = schemas
    this.sudocuProcedures = sudocuProcedures
    console.log('this.sudocuProcedures: ', this.sudocuProcedures)
    const { procedures, projects } = await this.$urbanisator.getProjectsProcedures(this.$route.params.collectiviteId)
    this.procedures = [...this.sudocuProcedures, ...procedures]
    this.projects = projects

    const test = await this.$urbanisator.getProjects(this.$route.params.collectiviteId)
    console.log('TESTING ', test)
  },
  methods: {
    async fetchProjects () {
      const { procedures, projects } = await this.$urbanisator.getProjectsProcedures(this.$route.params.collectiviteId)
      this.procedures = [...this.sudocuProcedures, ...procedures]
      this.projects = projects
    }
  }
}
</script>

<style lang="scss">
.border-light{
  border: solid 1px var(--v-primary-lighten1) !important;
}
</style>
