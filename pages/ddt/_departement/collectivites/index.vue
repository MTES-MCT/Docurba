<template>
  <v-container v-if="epcis && communes">
    <v-row>
      <!-- <v-col v-if="!clickedOnDocLink" cols="12"> -->
      <!-- <v-col cols="12">
        <v-alert type="info">
          Regardez le replay du Flash info du 18 avril :
          <a
            class="white--text"
            href="https://pad.incubateur.net/s/A_BpJ3_NH"
            target="_blank"
          >zoom sur les nouveautés et amélioration à venir.</a>
        </v-alert>
      </v-col> -->
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
              :items="epcis"
              :items-per-page="50"
              class="elevation-1"
              :custom-filter="customFilter"
              :search="search"
              :loading="!epcis"
              loading-text="Chargement des collectivités..."
            >
              <template #top />

              <!-- eslint-disable-next-line -->
            <template #item.competence="{ item }">
                <div v-if="item.competenceSudocu || item.competencePLU" class="d-flex">
                  <!-- <div class="competence-tag-sudocu mr-2" :style="{visibility: item.competenceSudocu ? 'visible' : 'hidden'}">
                    C <span class="caption text-lowercase">Sudocu</span>
                  </div> -->
                  <div class="competence-tag-banatic mr-2" :style="{visibility: item.competencePLU ? 'visible' : 'hidden'}">
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
                  <v-btn depressed color="primary" :to="item.path">
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
              :items-per-page="50"
              class="elevation-1"
              :loading="!communes"
              loading-text="Chargement des collectivités..."
              :custom-filter="customFilter"
              :search="search"
            >
              <!-- eslint-disable-next-line -->
            <template #item.intercommunalite="{ item }">

                <div v-if="item.code">
                  <nuxt-link :to="`/ddt/${item.departementCode}/collectivites/${item.code}/epci`">
                    {{ item.intitule }}
                  </nuxt-link>
                </div>
                <div v-else>
                  -
                </div>
              </template>

              <!-- eslint-disable-next-line -->
            <template #item.competence="{ item }">
                <div v-if="item.competenceSudocu || item.competencePLU" class="d-flex">
                  <div class="competence-tag-sudocu mr-2" :style="{visibility: item.competenceSudocu ? 'visible' : 'hidden'}">
                    C <span class="caption text-lowercase">Sudocu</span>
                  </div>
                  <div class="competence-tag-banatic mr-2" :style="{visibility: item.competencePLU ? 'visible' : 'hidden'}">
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
                  <v-btn depressed color="primary" :to="item.path">
                    Consulter
                  </v-btn>
                </div>
              </template>
            </v-data-table>
          </v-tab-item>
          <v-tab-item>
            <DashboardSCOTsDepList :search="search" />
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'

const docVersion = '1.0'

const tabs = {
  epci: 0,
  communes: 1,
  scot: 2
}

export default {
  name: 'CollectiviteDU',
  layout: 'ddt',
  data () {
    return {
      search: this.$route.query.search || '',
      lastProcedures: null,
      epcis: null,
      communes: null,
      scope: tabs[this.$route.query.tab] || 0,
      clickedOnDocLink: true
    }
  },
  computed: {
    headers () {
      return [
        { text: 'Nom', align: 'start', value: 'intitule', filterable: true },
        { text: 'Code INSEE', align: 'start', value: 'code', filterable: true },
        { text: 'Compétence', value: 'competence', filterable: false },
        { text: 'Intercommunalité', value: 'type', filterable: false },
        { text: 'Actions', value: 'actions', filterable: false }
      ]
    },
    headersEpci () {
      return [
        { text: 'Nom', align: 'start', value: 'intitule', filterable: true },
        { text: 'SIREN', align: 'start', value: 'code', filterable: true },
        { text: 'Type', value: 'type', filterable: false },
        { text: 'Compétence', value: 'competence', filterable: false },
        { text: 'Actions', value: 'actions', filterable: false }
      ]
    }
  },
  async mounted () {
    this.clickedOnDocLink = (localStorage.getItem('docVersion') === docVersion)

    const { data: collectivites } = await axios.get(`/api/geo/collectivites?departements=${this.$route.params.departement}`)
    this.epcis = collectivites.groupements.map(e => ({ ...e, path: `/ddt/${e.departementCode}/collectivites/${e.code}/epci` }))
    this.communes = collectivites.communes.map(e => ({ ...e, path: `/ddt/${e.departementCode}/collectivites/${e.codeParent || e.code}/commune` }))
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
