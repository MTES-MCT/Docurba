<template>
  <v-row>
    <v-col cols="12" class="pb-0">
      <v-row class="mt-6">
        <v-col cols="auto">
          <v-text-field
            v-model="search.text"
            dense
            outlined
            hide-details
            label="Recherche"
            :append-icon="icons.mdiMagnify"
          />
        </v-col>
        <v-spacer />
        <v-col cols="auto" class="interco-select">
          <v-select
            v-model="search.interco"
            placeholder="Intercommunalites"
            solo
            :items="intercommunalites"
            item-text="intitule"
            item-value="code"
            flat
            hide-details
            clearable
          />
        </v-col>
        <v-col cols="auto" class="status-select">
          <v-select v-model="search.status" solo :items="search.statusList" flat hide-details />
        </v-col>
      </v-row>
    </v-col>
    <v-col v-show="collectivities.length" cols="12" class="pt-0">
      <v-row>
        <v-col v-if="!showListLoader" cols="12">
          <v-list>
            <v-list-item-group v-model="selectedCollectivities" multiple>
              <template v-for="(collectivity, i) in filteredCollectivities">
                <ProceduresCollectivityListItem :key="collectivity.code" :collectivity="collectivity" :validated="validated" />
                <v-divider :key="i" />
              </template>
            </v-list-item-group>
          </v-list>
        </v-col>
        <v-col v-else>
          <VGlobalLoader />
        </v-col>
      </v-row>
      <v-row align="center">
        <v-col cols="4">
          <v-pagination v-model="page" :length="Math.ceil(searchedCollectivities.length/10)" class="pagination" />
        </v-col>
        <v-spacer />
        <v-col v-if="!validated" cols="auto" class="mr-2">
          <v-checkbox v-model="selectAll" hide-details class="d-flex align-center mt-0">
            <template #prepend>
              <div class="text-no-wrap primary--text">
                Tout valider
              </div>
            </template>
          </v-checkbox>
        </v-col>
      </v-row>
      <v-row v-if="!validated">
        <v-spacer />
        <v-col cols="auto" class="mr-4">
          <v-btn color="primary" :loading="loadingValidation" :disabled="!loadingValidation && selectedCollectivities.length === 0" @click="validateSelection">
            Valider {{
              selectedCollectivities.length ?
                `${selectedCollectivities.length} commune${selectedCollectivities.length > 1 ? 's' : ''}`
                : ''
            }}
          </v-btn>
        </v-col>
      </v-row>
    </v-col>
    <v-col v-show="!collectivities.length" cols="12">
      <v-row justify="center" class="my-5">
        <v-col cols="auto">
          <h4 class="text-h4">
            Aucune communes {{ validated ? 'validées' : 'à valider' }}
          </h4>
        </v-col>
      </v-row>
    </v-col>
  </v-row>
</template>

<script>
import { mdiMagnify } from '@mdi/js'

export default {
  props: {
    collectivities: {
      type: Array,
      required: true
    },
    validated: {
      type: Boolean,
      default: false
    },
    intercommunalites: {
      type: Array,
      default () { return [] }
    }
  },
  data () {
    return {
      search: {
        text: '',
        interco: '',
        status: 'all',
        statusList: [{
          text: 'Tous les statuts',
          value: 'all'
        }, {
          text: 'Opposable',
          value: 'opposable'
        }, {
          text: 'En cours',
          value: 'en cours'
        }]
      },
      icons: { mdiMagnify },
      selectedCollectivities: [],
      page: 1,
      selectAll: false,
      loadingValidation: false,
      fullyLoaded: false
    }
  },
  computed: {
    searchedCollectivities () {
      const normalizedSearch = this.search.text.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return this.collectivities.filter((collectivity) => {
        const normalizedValue = `${collectivity.intitule} ${collectivity.code}`.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

        if (normalizedSearch && !normalizedValue.includes(normalizedSearch)) {
          return false
        }

        if (this.search.interco && collectivity.intercommunaliteCode !== this.search.interco) {
          return false
        }

        if (this.search.status !== 'all' && collectivity.loaded) {
          const searchedProcedure = collectivity.procedures.find(p => p.status === this.search.status)
          if (!searchedProcedure) { return false }
        }

        return true
      })
    },
    filteredCollectivities () {
      const pageIndex = (this.page - 1) * 10
      return this.searchedCollectivities.slice(pageIndex, pageIndex + 10)
    },
    showListLoader () {
      return this.search.status !== 'all' ? !this.fullyLoaded : false
    },
    displayedCodes () {
      return this.filteredCollectivities.filter(c => !c.loaded).map(c => c.code)
    }
  },
  watch: {
    collectivities () {
      this.fetchCollectivitiesProcedures(this.displayedCodes)
    },
    searchedCollectivities () {
      if (this.page > (this.searchedCollectivities.length / 10)) {
        this.page = Math.ceil(this.searchedCollectivities.length / 10) || 1
      }
    },
    filteredCollectivities () {
      this.fetchCollectivitiesProcedures(this.displayedCodes)
    },
    selectAll () {
      if (this.selectAll) {
        this.selectedCollectivities = this.filteredCollectivities.map(c => c.code)
      } else {
        this.selectedCollectivities = []
      }
    },
    page () {
      // this.fetchCollectivitiesProcedures(this.displayedCodes)
      this.selectAll = false
    }
  },
  async mounted () {
    // First load the 10 first collectivities
    this.fetchCollectivitiesProcedures(this.filteredCollectivities.filter(c => !c.loaded).map(c => c.code))
    // Then load all for filters
    await this.fetchCollectivitiesProcedures(this.collectivities.filter(c => !c.loaded).map(c => c.code))
    this.fullyLoaded = true
  },
  methods: {
    async fetchCollectivitiesProcedures (codes) {
      // console.log('filteredCollectivities', this.filteredCollectivities)

      let { data: procedures } = await this.$supabase
        .rpc('procedures_by_insee_codes', {
          codes
        })

      procedures = procedures.filter(p => !p.archived)

      this.collectivities.filter(c => codes.includes(c.code)).forEach((collectivite) => {
        if (!collectivite.loaded) {
          collectivite.procedures = procedures.filter((procedure) => {
            return procedure.doc_type !== 'SCOT' && !!procedure.current_perimetre.find(c => c.inseeCode === collectivite.code)
          })

          collectivite.loaded = true
        }
      })
    },
    async validateSelection () {
      this.loadingValidation = true

      const validations = []

      this.selectedCollectivities.forEach((inseeCode) => {
        const collectivity = this.filteredCollectivities.find(c => c.code === inseeCode)

        collectivity.procedures.forEach((procedure) => {
          validations.push({
            collectivite_code: inseeCode,
            procedure_id: procedure.id,
            status: procedure.status,
            departement: collectivity.departementCode,
            doc_type: procedure.doc_type
          })
        })

        if (!collectivity.procedures.length) {
          validations.push({
            collectivite_code: inseeCode,
            status: 'RNU',
            departement: collectivity.departementCode,
            doc_type: 'RNU'
          })
        }
      })

      await this.$supabase.from('procedures_validations').insert(validations)

      this.$emit('validations', validations)

      this.loadingValidation = false
    }
  }
}
</script>

<style scoped>
.interco-select {
  max-width: 300px;
}

.status-select {
  max-width: 200px;
}
</style>

<style>
.pagination .v-pagination__item, .pagination .v-pagination__navigation {
  box-shadow:  0px 0px 0px rgba(0, 0, 0, 0.2), 0px 0px 0px 0px rgba(0, 0, 0, 0.14), 0px 0px 0px 0px rgba(0, 0, 0, 0.12) !important
}
</style>
