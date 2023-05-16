<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Tableau de bord - {{ $route.params.departement }}</h1>
      </v-col>
      <v-col cols="12">
        <div style="background-color: #F6F6F6;border: 1px solid #DDDDDD;border-radius:4px;" class="pa-6">
          <v-text-field
            v-model="search"
            filled
            hide-details=""
            dense
            style="max-width:500px"
            label="Rechercher"
          />
          <v-divider class="my-4" />
          <div class="d-flex">
            <v-select flat solo label="Compétence" :items="['Peut-importe', 'Oui', 'Non']" />
            <v-select flat solo label="Toutes procédures principales" :items="['Peut-importe', 'Oui', 'Non']" />
            <v-select flat solo label="Tous les status" :items="['Peut-importe', 'Oui', 'Non']" />
            <v-select flat solo label="Tous SCoT" :items="['Peut-importe', 'Oui', 'Non']" />
          </div>
        </div>
      </v-col>
      <v-col cols="12">
        <v-tabs v-model="scope">
          <v-tab>EPCI</v-tab>
          <v-tab>Communes</v-tab>
        </v-tabs>

        <v-tabs-items v-model="scope">
          <v-tab-item>
            <v-data-table
              :headers="headers"
              :items="collectivites"
              class="elevation-1"
              :search="search"
            >
              <template #top />
              <!-- eslint-disable-next-line -->
            <template #item.actions="{ item }">
                <div>
                  <v-btn depressed color="primary" :to="item.detailsPath">
                    Consulter
                  </v-btn>
                </div>
              </template>
            </v-data-table>
          </v-tab-item>
          <v-tab-item>
            <v-data-table
              v-if="communes"
              :headers="headers"
              :items="communes"
              class="elevation-1"
              :search="search"
            >
              <!-- eslint-disable-next-line -->
            <template #item.actions="{ item }">
                <div>
                  <v-btn depressed color="primary" :to="item.detailsPath">
                    Consulter
                  </v-btn>
                </div>
              </template>
            </v-data-table>
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      search: '',
      epci: null,
      communes: null,
      scope: 0
    }
  },
  computed: {
    headers () {
      return [
        { text: 'Collec. porteuse', align: 'start', value: 'name' },
        { text: 'Type', value: 'type' },
        { text: 'Dernière proc.', value: 'lastProc' },
        { text: 'Status', value: 'status' },
        { text: 'Actions', value: 'actions' }
      ]
    },
    collectivites () {
      if (!this.epci) { return [] }
      return this.epci.map((e) => {
        return {
          name: e.label,
          type: `EPCI (${e.towns.length})`,
          lastProc: '',
          status: '',
          detailsPath: { name: 'ddt-departement-collectivites-collectiviteId', params: { departement: this.$route.params.departement, collectiviteId: e.EPCI }, query: { isEpci: true } },
          frpProcPrincipalPath: { name: 'foo' }
        }
      })
    }
  },
  async mounted () {
    const { data: epcis } = await axios({
      url: '/api/epci',
      method: 'get',
      params: {
        departement: this.$route.params.departement
      }
    })

    const { data: communes } = await axios({
      url: '/api/communes',
      method: 'get',
      params: {
        departements: this.$route.params.departement
      }
    })

    this.epci = epcis

    console.log('communes: ', communes)
    this.communes = communes.map((e) => {
      return {
        name: e.nom_commune_complet,
        type: 'Commune',
        lastProc: '',
        status: '',
        detailsPath: { name: 'ddt-departement-collectivites-collectiviteId', params: { departement: this.$route.params.departement, collectiviteId: e.code_commune_INSEE }, query: { isEpci: false } },
        frpProcPrincipalPath: { name: 'foo' }
      }
    })

    console.log('EPCIs: ', this.epci)
  }
}
</script>
