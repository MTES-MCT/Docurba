<template>
  <v-container v-if="epcis && communes">
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
        <v-data-table
          :headers="headers"
          :items="epcis"
          :items-per-page="10"
          class="elevation-1 pa-8"
          :custom-filter="customFilter"
          :search="search"
          :loading="!epcis"
          loading-text="Chargement des collectivités..."
        >
          <template #top>
            <div class="d-flex  align-center justify-space-between">
              <v-select
                flat
                background-color="alt-beige"
                hide-details
                solo
                dense
                :items="['foo', 'bar']"
                style="max-width:150px"
              />
              <v-spacer />
              <v-text-field
                v-model="search"
                outlined
                hide-details
                dense
                style="max-width:400px"
                label="Rechercher une collectivité..."
              />
            </div>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.name="{ item }">
            <span>test</span>
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
        { text: 'Nom', align: 'start', value: 'name', filterable: true },
        { text: 'Type', align: 'start', value: 'type', filterable: true },
        { text: 'Procédures', value: 'procedures', filterable: false },
        { text: 'SCOTs', value: 'scots', filterable: false }
      ]
    }
  },
  async mounted () {
    this.clickedOnDocLink = (localStorage.getItem('docVersion') === docVersion)

    const { data: collectivites } = await axios.get(`/api/geo/collectivites?departements=${this.$route.params.departement}`)
    console.log('collec: ', collectivites)
    this.epcis = collectivites.groupements.map(e => ({ ...e, path: `/ddt/${e.departementCode}/collectivites/${e.code}/epci` }))
    this.communes = collectivites.communes.map(e => ({ ...e, path: `/ddt/${e.departementCode}/collectivites/${e.code}/commune` }))
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
