<template>
  <div v-if="collectivite">
    <v-container class="px-0 mt-8">
      <v-row align="end" class="mb-1">
        <v-col cols="auto">
          <nuxt-link class="text-decoration-none d-flex align-center" :to="`/ddt/${$route.params.departement}/collectivites/${$route.params.collectiviteId}/${$route.params.collectiviteId.length > 5 ? 'epci' : 'commune'}`">
            <v-icon color="primary" small class="mr-2">
              {{ icons.mdiChevronLeft }}
            </v-icon>
            {{ collectivite.intitule }}
          </nuxt-link>
          <h1>Nouvelle procédure</h1>
        </v-col>
      </v-row>
    </v-container>
    <v-container class="border-grey pb-8 px-8 mb-16">
      <v-row>
        <v-col cols="12" class="pt-0 pb-8">
          <v-tabs v-model="tab" class="py-4">
            <v-tab>Procédure principale</v-tab>
            <v-tab>Procédure secondaire</v-tab>
          </v-tabs>
        </v-col>
      </v-row>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <DdtAddProcedureForm :collectivite="collectivite" procedure-category="principale" />
        </v-tab-item>
        <v-tab-item>
          <DdtAddProcedureForm :collectivite="collectivite" procedure-category="secondaire" />
        </v-tab-item>
      </v-tabs-items>
    </v-container>
  </div>
</template>
<script>
import axios from 'axios'
import { mdiChevronLeft } from '@mdi/js'
export default {
  name: 'ProcedureAdd',
  layout: 'ddt',
  data () {
    return {
      collectivite: null,
      tab: null,
      icons: { mdiChevronLeft }
    }
  },
  async mounted () {
    this.collectivite = (await axios({
      url: `/api/geo/${this.$route.params.collectiviteId.length > 5 ? 'intercommunalites' : 'communes'}/${this.$route.params.collectiviteId}`,
      method: 'get'
    })).data
    console.log('collectivite: ', this.collectivite)
  }
}
</script>
