<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <LayoutsBannerAlert />
      </v-col>
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
                    Tout type de collectivité
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
                <v-chip v-if="item.type === 'COM'" class="ml-2 error--text font-weight-bold" small label color="error-light">
                  RNU
                </v-chip>
                <span v-else>-</span>
              </div>
              <div v-for="(plan, index) in item.plans" :key="plan.id" class="mb-4">
                <template v-if="index < 2">
                  <nuxt-link class="font-weight-bold text-decoration-none" :to="`/frise/${plan.id}`">
                    {{ plan.doc_type }}
                  </nuxt-link>
                  <v-chip
                    :class="{
                      'success-light': plan.inContextStatus === 'OPPOSABLE',
                      'success--text': plan.inContextStatus === 'OPPOSABLE',
                      'bf200': plan.inContextStatus === 'EN COURS',
                      'primary--text': plan.inContextStatus === 'EN COURS',
                      'text--lighten-2': plan.inContextStatus === 'EN COURS',

                    }"
                    class="ml-2 font-weight-bold "
                    small
                    label
                  >
                    {{ plan.inContextStatus }}
                  </v-chip>
                </template>
                <nuxt-link v-else-if="index === 2" class="font-weight-bold text-decoration-none" :to="`/ddt/${item.departementCode}/collectivites/${item.code}/${item.code.length > 5 ? 'epci' : 'commune'}`">
                  + {{ item.plans.length - 2 }} procédure{{ item.plans.length - 2 > 1 ? 's' : '' }}
                </nuxt-link>
              </div>
            </div>
          </template>
          <!-- eslint-disable-next-line -->
          <template #item.scots="{ item }">
            <div v-if="!item.scots || item.scots.length === 0" class="my-6">
              -
            </div>
            <!-- <div v-for="scot in item.scots" :key="scot.id">
              <nuxt-link class="font-weight-bold text-decoration-none" :to="`/frise/${scot.id}`">
                {{ scot.doc_type }}
              </nuxt-link>
               &nbsp;
              {{ scot.id }}
            </div> -->

            <div class="my-5">
              <div v-if="!item.scots || item.scots.length === 0">
                -
              </div>
              <div v-for="(scot, index) in item.scots" v-else :key="scot.id" class="mb-4">
                <template v-if="index < 2">
                  <nuxt-link class="font-weight-bold text-decoration-none" :to="`/frise/${scot.id}`">
                    {{ scot.doc_type }}
                  </nuxt-link>
                  <v-chip
                    :class="{
                      'success-light': scot.inContextStatus === 'OPPOSABLE',
                      'success--text': scot.inContextStatus === 'OPPOSABLE',
                      'bf200': scot.inContextStatus === 'EN COURS',
                      'primary--text': scot.inContextStatus === 'EN COURS',
                      'text--lighten-2': scot.inContextStatus === 'EN COURS',

                    }"
                    class="ml-2 font-weight-bold "
                    small
                    label
                  >
                    {{ scot.inContextStatus }}
                  </v-chip>
                </template>
                <nuxt-link v-else-if="index === 2" class="font-weight-bold text-decoration-none" :to="`/ddt/${item.departementCode}/collectivites/${item.code}/${item.code.length > 5 ? 'epci' : 'commune'}`">
                  + {{ item.scots.length - 2 }} procédure{{ item.scots.length - 2 > 1 ? 's' : '' }}
                </nuxt-link>
              </div>
            </div>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
const docVersion = '1.0'

const statusMap = {
  opposable: 'OPPOSABLE',
  'en cours': 'EN COURS'
}

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
        { text: 'Type', align: 'start', value: 'type', filterable: false, width: '10%' },
        { text: 'Procédures', value: 'procedures', filterable: false, sortable: false, width: '30%' },
        { text: 'SCOTs', value: 'scots', filterable: false, sortable: false, width: '30%' }
      ]
    },
    collectivites () {
      return this.referentiel?.filter(e => this.selectedCollectiviteTypesFilter.includes(e.type))
    }
  },
  async mounted () {
    const referentiel = await fetch(`/api/geo/collectivites?departements=${this.$route.params.departement}`)
    const { communes, groupements } = await referentiel.json()
    const procedures = await this.$urbanisator.getCollectivitesProcedures(communes.map(c => c.code))

    const enrichedCommunes = this.parseCommunes(communes, procedures)
    const enrichedGroups = this.parseGroupements(groupements, procedures)

    this.referentiel = [...enrichedGroups, ...enrichedCommunes]
  },
  methods: {
    parseCommunes (communes, procedures) {
      return communes.map((commune) => {
        const communeProcedures = procedures.filter((procedure) => {
          return !!procedure.procedures_perimetres.find((p) => {
            return p.collectivite_code === commune.code
          })
        })

        const inContextProcedures = communeProcedures.map((procedure) => {
          const isOpposableInContext = procedure.procedures_perimetres.find((p) => {
            return p.collectivite_code === commune.code && p.opposable
          })

          let status = procedure.status

          if (status === 'opposable' && !isOpposableInContext) {
            status = 'precedent'
          }

          return Object.assign({}, procedure, {
            status,
            inContextStatus: statusMap[status] || 'ARCHIVÉ'
          })
        }).sort((a, b) => {
          if (a.inContextStatus < b.inContextStatus) { return -1 }
          if (a.inContextStatus > b.inContextStatus) { return 1 }
          return 0
        }).reverse()

        return {
          ...commune,
          plans: inContextProcedures.filter(p => p.doc_type !== 'SCOT'),
          scots: inContextProcedures.filter(p => p.doc_type === 'SCOT')
        }
      })
    },
    parseGroupements (groupements, procedures) {
      return groupements.map((groupement) => {
        const collectivitesSet = new Set(groupement.membres.map(m => m.code))
        const groupementProcedures = procedures.filter((procedure) => {
          return procedure.procedures_perimetres.map(p => p.collectivite_code).some((code) => {
            return collectivitesSet.has(code)
          })
        })

        const inContextProcedures = groupementProcedures.map((procedure) => {
          return Object.assign({}, procedure, {
            inContextStatus: statusMap[procedure.status] || 'ARCHIVÉ'
          })
        }).sort((a, b) => {
          if (a.inContextStatus < b.inContextStatus) { return -1 }
          if (a.inContextStatus > b.inContextStatus) { return 1 }
          return 0
        }).reverse()

        return {
          ...groupement,
          plans: inContextProcedures.filter(p => p.doc_type !== 'SCOT' && p.procedures_perimetres.length > 1),
          scots: inContextProcedures.filter(p => p.doc_type === 'SCOT')
        }
      })
    },
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
