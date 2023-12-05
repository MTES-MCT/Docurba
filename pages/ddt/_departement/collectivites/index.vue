<template>
  <v-container>
    <v-row>
      <v-col v-if="!clickedOnDocLink" cols="12">
        <v-alert type="info">
          Zoom sur les dernières améliorations des fonctionnalités de Docurba.
          <a
            class="white--text"
            href="https://pad.incubateur.net/FUz6ITnHSC6wVv1rvIipyg?view"
            target="_blank"
            @click="showClose"
          >Découvrez la documentation</a>
        </v-alert>
      </v-col>
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
              :custom-filter="customFilter"
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
              :custom-filter="customFilter"
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

const docVersion = '1.0'

export default {
  name: 'CollectiviteDU',
  layout: 'ddt',
  data () {
    return {
      search: '',
      lastProcedures: null,
      epci: null,
      communes: null,
      scope: 0,
      clickedOnDocLink: true
    }
  },
  computed: {
    headers () {
      return [
        { text: 'Nom', align: 'start', value: 'name', filterable: true },
        { text: 'Code INSEE', align: 'start', value: 'code', filterable: true },
        { text: 'Compétence', value: 'competence', filterable: false },
        { text: 'Intercommunalité', value: 'intercommunalite', filterable: false },
        // { text: 'Date de création', value: 'dateCreation' },
        { text: 'Actions', value: 'actions', filterable: false }
      ]
    },
    headersEpci () {
      return [
        { text: 'Nom', align: 'start', value: 'name', filterable: true },
        { text: 'SIREN', align: 'start', value: 'code', filterable: true },
        { text: 'Type', value: 'type', filterable: false },
        { text: 'Compétence', value: 'competence', filterable: false },
        // { text: 'Date de création', value: 'dateCreation' },
        { text: 'Actions', value: 'actions', filterable: false }
      ]
    },
    collectivites () {
      if (!this.epci) { return [] }

      return this.epci.map((collectivite) => {
        return {
          name: collectivite.intitule,
          code: collectivite.code,
          competenceSudocu: collectivite.hasCompetence,
          competenceBanatic: collectivite.competences.plu,
          // dateCreation: collectivite.dateCreation,
          type: `${collectivite.labelJuridique} (${collectivite.nbCommunes})`,
          lastProc: '',
          status: '',
          detailsPath: {
            name: 'ddt-departement-collectivites-collectiviteId-epci',
            params: {
              departement: this.$route.params.departement,
              collectiviteId: collectivite.code
            }
          },
          frpProcPrincipalPath: { name: 'foo' }
        }
      })
    }
  },
  async mounted () {
    this.clickedOnDocLink = (localStorage.getItem('docVersion') === docVersion)

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

    // eslint-disable-next-line no-console
    if (errorSudocuCollectivites) { console.log('errorSudocuCollectivites: ', errorSudocuCollectivites) }

    this.epci = epcis.map((e) => {
      const sudoEpci = sudocuCollectivites.find((i) => {
        return i.codecollectivite === e.code
      })
      // if (!sudoEpci) {
      //   // console.log('not found sudoEpci: ', e)
      // }
      // // console.log('sudoEpci: ', sudoEpci)
      return {
        ...e,
        hasCompetence: sudoEpci?.sicompetenceplan ?? false
      }
    })

    const communesUniq = [...new Map(communes.map(item => [item.code, item])).values()]
    // console.log('this.epci ici: ', communesUniq, ' sudocuCollectivites: ', sudocuCollectivites)
    this.communes = communesUniq.map((commune) => {
      const sudoCom = sudocuCollectivites.find(i => i.codecollectivite === commune.code)
      // if (!sudoCom) {
      //   consolcommune.log('not found: ', e)
      // }
      // consolcommune.log('sudoCom: ', sudoCom)
      return {
        name: commune.intitule,
        code: commune.code,
        competenceSudocu: sudoCom?.sicompetenceplan,
        competenceBanatic: commune.competencePLU,
        type: 'Commune',
        lastProc: '',
        status: '',
        intercommunaliteName: commune.intercommunaliteName,
        departementCode: commune.departementCode,
        // dateCreation: commune.dateCreation,
        intercommunaliteCode: commune.intercommunaliteCode,
        detailsPath: {
          name: 'ddt-departement-collectivites-collectiviteId-commune',
          params: {
            departement: this.$route.params.departement,
            collectiviteId: commune.code
          }
        },
        frpProcPrincipalPath: { name: 'foo' }
      }
    })
  },
  methods: {
    customFilter (value, search, item) {
      if (!search?.length || !value?.length) { return true }

      const normalizedValue = value.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
      const normalizedSearch = search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return normalizedValue.includes(normalizedSearch)
    },
    showClose () {
      this.clickedOnDocLink = true
      localStorage.setItem('docVersion', docVersion)
    }
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
