<template>
  <v-container v-if="collectivite">
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
    <template v-if="loaded">
      <v-row>
        <v-col cols="12">
          <v-alert type="info">
            L'extract de données Sudocuh vers Docurba est désormais journalier, les données sur Docurba sont donc à jour.
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
        :procedures="plans"
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
      tab: null,
      collectivite: null,
      plans: [],
      schemas: [],
      icons: { mdiArrowLeft }
    }
  },
  async mounted () {
    await this.getProcedures()
    this.loaded = true
  },
  methods: {
    async getProcedures () {
      console.log('getProcedures')
      this.collectivite = (await axios({ url: `/api/geo/collectivites/${this.$route.params.collectiviteId}` })).data
      console.log('api collectivite')
      const { plans, schemas } = await this.$urbanisator.getProjects(this.$route.params.collectiviteId)
      this.schemas = schemas
      this.plans = plans
      console.log('schemas: ', schemas, ' plans: ', plans)
    }
  }
}
</script>

<style lang="scss">
.border-light{
  border: solid 1px var(--v-primary-lighten1) !important;
}
</style>
