<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Mes collectivités - {{ $route.params.departement }}</h1>
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
          <!-- <v-divider class="my-4" />
          <div class="d-flex">
            <v-select flat solo label="Compétence" :items="['Peut-importe', 'Oui', 'Non']" />
            <v-select flat solo label="Toutes procédures principales" :items="['Peut-importe', 'Oui', 'Non']" />
            <v-select flat solo label="Tous les status" :items="['Peut-importe', 'Oui', 'Non']" />
            <v-select flat solo label="Tous SCoT" :items="['Peut-importe', 'Oui', 'Non']" />
          </div> -->
        </div>
      </v-col>
      <v-col cols="12">
        <v-tabs v-model="scope">
          <v-tab>EPCI</v-tab>
          <v-tab>Communes</v-tab>
          <v-tab>SCOTs</v-tab>
        </v-tabs>

        <v-tabs-items v-model="scope">
          <v-tab-item>
            <v-data-table
              :headers="headersEpci"
              :items="collectivites"
              class="elevation-1"
              :search="search"
              :loading="!epci"
              loading-text="Chargement des collectivités..."
            >
              <template #top />

              <!-- eslint-disable-next-line -->
            <template #item.competence="{ item }">
                <div v-if="item.competenceSudocu || item.competenceBanatic" class="d-flex">
                  <div class="competence-tag-sudocu mr-2" :style="{visibility: item.competenceSudocu ? 'visible' : 'hidden'}">
                    C <span class="caption text-lowercase">Sudocu</span>
                  </div>
                  <div class="competence-tag-banatic mr-2" :style="{visibility: item.competenceBanatic ? 'visible' : 'hidden'}">
                    C <span class="caption text-lowercase">BANATIC</span>
                  </div>
                </div>
                <div v-else>
                  -
                </div>
              </template>
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
              :loading="!communes"
              loading-text="Chargement des collectivités..."
              :search="search"
            >
              <!-- eslint-disable-next-line -->
            <template #item.intercommunalite="{ item }">

                <div v-if="item.intercommunaliteCode">
                  <nuxt-link :to="`/ddt/${item.departementCode}/collectivites/${item.intercommunaliteCode}/epci`">
                    {{ item.intercommunaliteName }}
                  </nuxt-link>
                </div>
                <div v-else>
                  -
                </div>
              </template>

              <!-- eslint-disable-next-line -->
            <template #item.competence="{ item }">
                <div v-if="item.competenceSudocu || item.competenceBanatic" class="d-flex">
                  <div class="competence-tag-sudocu mr-2" :style="{visibility: item.competenceSudocu ? 'visible' : 'hidden'}">
                    C <span class="caption text-lowercase">Sudocu</span>
                  </div>
                  <div class="competence-tag-banatic mr-2" :style="{visibility: item.competenceBanatic ? 'visible' : 'hidden'}">
                    C <span class="caption text-lowercase">BANATIC</span>
                  </div>
                </div>
                <div v-else>
                  -
                </div>
              </template>

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
            <DashboardSCOTsDepList />
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CollectiviteDU',
  layout: 'ddt',
  data () {
    return {
      search: '',
      lastProcedures: null,
      epci: null,
      communes: null,
      scope: 0
    }
  },
  computed: {
    headers () {
      return [
        { text: 'Nom', align: 'start', value: 'name' },
        { text: 'Compétence', value: 'competence' },
        { text: 'Intercommunalité', value: 'intercommunalite' },
        { text: 'Date de création', value: 'dateCreation' },
        { text: 'Actions', value: 'actions' }
      ]
    },
    headersEpci () {
      return [
        { text: 'Nom', align: 'start', value: 'name' },
        { text: 'Type', value: 'type' },
        { text: 'Compétence', value: 'competence' },
        { text: 'Date de création', value: 'dateCreation' },
        { text: 'Actions', value: 'actions' }
      ]
    },
    collectivites () {
      if (!this.epci) { return [] }

      return this.epci.map((e) => {
        return {
          name: e.intitule,
          competenceSudocu: e.hasCompetence,
          competenceBanatic: e.competences.plu,
          dateCreation: e.dateCreation,
          type: `${e.labelJuridique} (${e.nbCommunes})`,
          lastProc: '',
          status: '',
          detailsPath: { name: 'ddt-departement-collectivites-collectiviteId-epci', params: { departement: this.$route.params.departement, collectiviteId: e.code } },
          frpProcPrincipalPath: { name: 'foo' }
        }
      })
    }
  },
  async mounted () {
    const { data: epcis } = await axios({
      url: '/api/geo/intercommunalites',
      method: 'get',
      params: {
        departementCode: this.$route.params.departement
      }
    })

    const { data: communes } = await axios({
      url: '/api/geo/communes',
      method: 'get',
      params: {
        departementCode: this.$route.params.departement
      }
    })

    const collecsInsee = communes.map(e => e.code.padStart(5, '0')).concat(epcis.map(e => e.code))
    const { data: sudocuCollectivites, error: errorSudocuCollectivites } = await this.$supabase.from('sudocu_collectivites').select().in('codecollectivite', collecsInsee)
    if (errorSudocuCollectivites) { console.log('errorSudocuCollectivites: ', errorSudocuCollectivites) }

    this.epci = epcis.map((e) => {
      const sudoEpci = sudocuCollectivites.find((i) => {
        return i.codecollectivite === e.code
      })
      if (!sudoEpci) {
        console.log('not found sudoEpci: ', e)
      }
      console.log('sudoEpci: ', sudoEpci)
      return {
        ...e,
        hasCompetence: sudoEpci?.sicompetenceplan ?? false
      }
    })

    const communesUniq = [...new Map(communes.map(item => [item.code, item])).values()]
    // console.log('this.epci ici: ', communesUniq, ' sudocuCollectivites: ', sudocuCollectivites)
    this.communes = communesUniq.map((e) => {
      const sudoCom = sudocuCollectivites.find(i => i.codecollectivite === e.code)
      // if (!sudoCom) {
      //   console.log('not found: ', e)
      // }
      // console.log('sudoCom: ', sudoCom)
      return {
        name: e.intitule,
        competenceSudocu: sudoCom?.sicompetenceplan,
        competenceBanatic: e.competencePLU,
        type: 'Commune',
        lastProc: '',
        status: '',
        intercommunaliteName: e.intercommunaliteName,
        departementCode: e.departementCode,
        dateCreation: e.dateCreation,
        intercommunaliteCode: e.intercommunaliteCode,
        detailsPath: { name: 'ddt-departement-collectivites-collectiviteId-commune', params: { departement: this.$route.params.departement, collectiviteId: e.code } },
        frpProcPrincipalPath: { name: 'foo' }
      }
    })
  }
}
</script>
<style lang="scss">
.competence-tag-sudocu{
  background: #FEECC2;
  border-radius: 4px;
  text-transform: uppercase;
  color: #716043;
  font-family: 'Marianne';
  font-style: normal;
  font-weight: 700;
  font-size: 14px;
  line-height: 24px;
  padding: 0px 8px;
}

.competence-tag-banatic{
  background: var(--v-primary-base);
  border-radius: 4px;
  text-transform: uppercase;
  color: var(--v-primary-lighten1);
  font-family: 'Marianne';
  font-style: normal;
  font-weight: 700;
  font-size: 14px;
  line-height: 24px;
  padding: 0px 8px;
}

</style>
