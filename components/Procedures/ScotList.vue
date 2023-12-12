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
        <v-col cols="auto" class="status-select">
          <v-select v-model="search.status" solo :items="search.statusList" flat hide-details />
        </v-col>
      </v-row>
    </v-col>
    <v-col v-if="loaded" cols="12" class="pt-0">
      <v-row>
        <v-col cols="12">
          <v-list>
            <v-list-item-group v-model="selectedScots" multiple>
              <template v-for="(scot, i) in filteredScots">
                <ProceduresScotListItem :key="scot.code" :scot="scot" :validated="validated" />
                <v-divider :key="i" />
              </template>
            </v-list-item-group>
          </v-list>
        </v-col>
      </v-row>
      <v-row v-show="loaded && scots.length" align="center">
        <v-col cols="4">
          <v-pagination v-model="page" :length="Math.ceil(searchedScots.length/10)" class="pagination" />
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
          <v-btn color="primary" :loading="loadingValidation" :disabled="!loadingValidation && selectedScots.length === 0" @click="validateSelection">
            Valider {{
              selectedScots.length ?
                `${selectedScots.length} SCOT`
                : ''
            }}
          </v-btn>
        </v-col>
      </v-row>
    </v-col>
    <v-col v-else>
      <VGlobalLoader />
    </v-col>
    <v-col v-show="loaded && !scots.length" cols="12">
      <v-row justify="center" class="my-5">
        <v-col cols="auto">
          <h4 class="text-h4">
            Aucun SCOT {{ validated ? 'validé' : 'à valider' }}
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
    scots: {
      type: Array,
      required: true
    },
    validated: {
      type: Boolean,
      default: false
    },
    loaded: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      search: {
        text: '',
        status: 'all',
        statusList: [{
          text: 'Tous les status',
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
      selectedScots: [],
      page: 1,
      selectAll: false,
      loadingValidation: false
    }
  },
  computed: {
    searchedScots () {
      const normalizedSearch = this.search.text.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return this.scots.filter((scot) => {
        if (normalizedSearch) {
          const normalizedValue = `${scot.intitule} ${scot.code}`.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
          if (!normalizedValue.includes(normalizedSearch)) { return false }
        }

        if (this.search.status !== 'all') {
          const searchedProcedure = scot.procedures.find(p => p.status === this.search.status)
          if (!searchedProcedure) { return false }
        }

        return true
      })
    },
    filteredScots () {
      const pageIndex = (this.page - 1) * 10
      return this.searchedScots.slice(pageIndex, pageIndex + 10)
    }
  },
  watch: {
    searchedScots () {
      if (this.page > (this.searchedScots.length / 10)) {
        this.page = Math.ceil(this.searchedScots.length / 10) || 1
      }
    },
    selectAll () {
      if (this.selectAll) {
        this.selectedScots = this.filteredScots.map(c => c.code)
      } else {
        this.selectedScots = []
      }
    },
    page () {
      this.selectAll = false
    }
  },
  methods: {
    async validateSelection () {
      this.loadingValidation = true

      const validations = []

      this.selectedScots.forEach((collectivityCode) => {
        const collectivity = this.filteredScots.find(c => c.code === collectivityCode)

        collectivity.procedures.forEach((procedure) => {
          validations.push({
            collectivite_code: collectivityCode,
            procedure_id: procedure.id,
            status: procedure.status,
            departement: this.$route.params.departement,
            doc_type: 'SCOT'
          })
        })
      })

      await this.$supabase.from('procedures_validations').insert(validations)
      this.$emit('validations', validations)

      this.loadingValidation = false
    }
  }
}
</script>

<style scoped>
.status-select {
  max-width: 200px;
}
</style>

<style>
.pagination .v-pagination__item, .pagination .v-pagination__navigation {
  box-shadow:  0px 0px 0px rgba(0, 0, 0, 0.2), 0px 0px 0px 0px rgba(0, 0, 0, 0.14), 0px 0px 0px 0px rgba(0, 0, 0, 0.12) !important
}
</style>
