<template>
  <v-container>
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
      <v-col v-if="!collectivites" cols="12">
        <v-skeleton-loader
          type="table"
        />
      </v-col>
      <v-col v-else cols="12">
        <v-data-table
          :headers="headers"
          :items="collectivites"
          :items-per-page="10"
          class="elevation-1 pa-8 collectivites-dt"
          :custom-filter="customFilter"
          :custom-sort="customSort"
          :search="search"
          :loading="!collectivites"
          loading-text="Chargement des collectivités..."
        >
          <template #top>
            <div class="d-flex align-center justify-space-between mb-6">
              <v-select
                v-model="selectedCollectiviteTypesFilter"
                flat
                background-color="alt-beige"
                hide-details
                solo
                multiple
                dense
                :items="collectiviteTypeFilterItems"
                style="max-width:350px"
              >
                <template #selection="{item, index}">
                  <div v-if="collectiviteTypeFilterItems.length === selectedCollectiviteTypesFilter.length && index === 0">
                    Tous types de collectivité
                  </div>
                  <span v-else-if="collectiviteTypeFilterItems.length !== selectedCollectiviteTypesFilter.length">
                    {{ item.text }}<span v-if="index !== selectedCollectiviteTypesFilter.length - 1">,&nbsp;</span>
                  </span>
                </template>
              </v-select>
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
            <div class="my-5">
              <nuxt-link :to="`/ddt/${item.departementCode}/collectivites/${item.code}/${item.code.length > 5 ? 'epci' : 'commune'}`" class="text-decoration-none font-weight-bold">
                {{ item.code }} {{ item.intitule }}
              </nuxt-link>
            </div>
          </template>
          <!-- eslint-disable-next-line -->
                 <template #item.type="{ item }">
            <div class="my-5">
              {{ item.type }}
            </div>
          </template>
          <!-- eslint-disable-next-line -->
            <template #item.procedures="{ item }">
            <div class="my-5">
              <div v-if="!item.plans || item.plans.length === 0">
                <v-chip class="ml-2 error--text font-weight-bold" small label color="error-light">
                  RNU
                </v-chip>
              </div>
              <div v-for="(plan, index) in item.plans" :key="plan.id" class="mb-4">
                <template v-if="index < 2">
                  <nuxt-link class="font-weight-bold text-decoration-none" :to="`/frise/${plan.id}`">
                    {{ plan.doc_type }}
                    <!-- {{ plan.id }} -->
                  </nuxt-link>

                  <v-chip v-if="plan.opposable" class="ml-2 success--text font-weight-bold" small label color="success-light">
                    OPPOSABLE
                  </v-chip>
                  <v-chip v-else-if="!plan.opposable && plan.status === 'opposable'" class="ml-2 font-weight-bold" small label>
                    ARCHIVÉ
                  </v-chip>
                  <v-chip v-else class="ml-2 primary--text text--lighten-2 font-weight-bold" small label color="bf200">
                    EN COURS
                  </v-chip>
                </template>
                <nuxt-link v-else-if="index === 2" class="font-weight-bold text-decoration-none" :to="`/ddt/${item.departementCode}/collectivites/${item.code}/${item.code.length > 5 ? 'epci' : 'commune'}`">
                  + {{ item.plans.length - 2 }} procédures
                </nuxt-link>
              </div>
            </div>
          </template>
          <!-- eslint-disable-next-line -->
          <template #item.scots="{ item }">
            <div v-if="!item.scots || item.scots.length === 0" class="my-6">
              -
            </div>
            <div v-for="scot in item.scots" :key="scot.id">
              {{ scot.doc_type }} &nbsp;
              {{ scot.id }}
            </div>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { groupBy, filter } from 'lodash'
const docVersion = '1.0'
export default {
  name: 'CollectiviteDU',
  layout: 'ddt',
  data () {
    return {
      selectedCollectiviteTypesFilter: ['COM', 'CA', 'CC', 'EPT', 'SM', 'SIVU', 'PETR'],
      collectiviteTypeFilterItems: [
        { text: 'Communes', value: 'COM' },
        { text: 'CA', value: 'CA' },
        { text: 'CC', value: 'CC' },
        { text: 'EPT', value: 'EPT' },
        { text: 'SM', value: 'SM' },
        { text: 'SIVU', value: 'SIVU' },
        { text: 'PETR', value: 'PETR' }
      ],
      search: this.$route.query.search || '',
      referentiel: null,
      clickedOnDocLink: true
    }
  },
  computed: {
    headers () {
      return [
        { text: 'Nom', align: 'start', value: 'name', filterable: true, width: '30%' },
        { text: 'Type', align: 'start', value: 'type', filterable: true, width: '10%' },
        { text: 'Procédures', value: 'procedures', filterable: false, sortable: false, width: '30%' },
        { text: 'SCOTs', value: 'scots', filterable: false, sortable: false, width: '30%' }
      ]
    },
    collectivites () {
      return this.referentiel?.filter(e => this.selectedCollectiviteTypesFilter.includes(e.type))
    }
  },
  async mounted () {
    const rawProcedures = this.$urbanisator.getProceduresByCommunes(this.$route.params.departement)
    const rawReferentiel = fetch(`/api/geo/collectivites?departements=${this.$route.params.departement}`)

    const [procedures, referentiel] = await Promise.all([rawProcedures, rawReferentiel])
    const { communes, groupements } = await referentiel.json()
    // TODO: Faire la meme chose sur les SCoTs
    const enrichedGroups = groupements.map((groupement) => {
      const proceduresGroupement = groupement.membres.map(membre => procedures[membre.code]?.plans).flat().filter(e => e)
      const perimetre = groupBy(proceduresGroupement, e => e.procedure_id)
      const proceduresPerimInter = filter(perimetre, e => e.length > 1)
      const proceduresInter = proceduresPerimInter.map(e => e?.[0].procedures)
      return { ...groupement, plans: proceduresInter }
    })

    const enrichedCommunes = communes.map(e => ({
      ...e,
      plans: procedures[e.code]?.plans.map((y) => {
        const proc = y.procedures
        return { ...proc, opposable: y.opposable }
      }),
      scots: procedures[e.code]?.scots.map(y => y.procedures)
    }))
    const flattenReferentiel = [...enrichedGroups, ...enrichedCommunes]
    this.referentiel = flattenReferentiel
  },
  methods: {
    customFilter (value, search, item) {
      if (!search?.length) { return true }
      const itemValue = item.intitule + item.code
      const normalizedValue = itemValue.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
      const normalizedSearch = search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return normalizedValue.includes(normalizedSearch)
    },
    customSort (items, index, isDesc) {
      items.sort((a, b) => {
        if (index[0] === 'name' || index[0] === 'type') {
          if (!isDesc[0]) {
            return a.code.toLowerCase().localeCompare(b.code.toLowerCase())
          } else {
            return b.code.toLowerCase().localeCompare(a.code.toLowerCase())
          }
        }
        return true
      })
      return items
    },
    showClose () {
      this.clickedOnDocLink = true
      localStorage.setItem('docVersion', docVersion)
    }
  }
}
</script>

<style lang="scss">
.collectivites-dt {
  tr th{
    font-size: 14px !important;
    color: #000 !important;
  }
   tbody tr td{
    vertical-align: top !important;
   }
}

</style>
