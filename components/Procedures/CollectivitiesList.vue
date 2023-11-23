<template>
  <v-row>
    <v-col v-show="collectivities.length" cols="12">
      <v-row>
        <v-col cols="12">
          <v-list>
            <v-list-item-group v-model="selectedCollectivities" multiple>
              <template v-for="(collectivity, i) in filteredCollectivities">
                <ProceduresCollectivityListItem :key="collectivity.code" :collectivity="collectivity" :validated="validated" />
                <v-divider :key="i" />
              </template>
            </v-list-item-group>
          </v-list>
        </v-col>
      </v-row>
      <v-row align="center">
        <v-col cols="4">
          <v-pagination v-model="page" :length="Math.ceil(collectivities.length/10)" class="pagination" />
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
export default {
  props: {
    collectivities: {
      type: Array,
      required: true
    },
    validated: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      collectivitiesList: this.collectivities.map(c => Object.assign({}, c)),
      selectedCollectivities: [],
      page: 1,
      selectAll: false,
      loadingValidation: false
    }
  },
  computed: {
    filteredCollectivities () {
      const pageIndex = (this.page - 1) * 10
      return this.collectivitiesList.slice(pageIndex, pageIndex + 10)
    }
  },
  watch: {
    collectivities () {
      this.collectivitiesList = this.collectivities.map((collectivity) => {
        const listItem = this.collectivitiesList.find(c => c.code === collectivity.code)
        return Object.assign({}, collectivity, listItem)
      })

      this.fetchCollectivitiesProcedures()
    },
    selectAll () {
      if (this.selectAll) {
        this.selectedCollectivities = this.filteredCollectivities.map(c => c.code)
      } else {
        this.selectedCollectivities = []
      }
    },
    page () {
      this.fetchCollectivitiesProcedures()
      this.selectAll = false
    }
  },
  mounted () {
    this.fetchCollectivitiesProcedures()
  },
  methods: {
    fetchCollectivitiesProcedures () {
      // console.log('filteredCollectivities', this.filteredCollectivities)

      this.filteredCollectivities.forEach(async (collectivite) => {
        // console.log(collectivite.procedures, !collectivite.procedures.length)
        if (!collectivite.procedures.length) {
          const inseeCode = collectivite.code

          const { data: procedures } = await this.$supabase.from('procedures')
            .select('id, status, doc_type, current_perimetre, is_pluih')
            .contains('current_perimetre', `[{ "inseeCode": "${inseeCode}" }]`)
            .in('status', ['opposable', 'en cours'])
            .eq('is_principale', true)

          procedures.forEach((procedure) => {
            if (procedure.doc_type === 'PLU' && procedure.current_perimetre.length > 1) {
              procedure.doc_type += 'i'

              if (procedure.is_pluih) {
                procedure.doc_type += 'h'
              }
            }
          })

          collectivite.procedures = procedures.filter(p => p.doc_type !== 'SCOT')
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
            insee_code: inseeCode,
            procedure_id: procedure.id,
            status: procedure.status,
            departement: collectivity.departementCode
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

<style>
.pagination .v-pagination__item, .pagination .v-pagination__navigation {
  box-shadow:  0px 0px 0px rgba(0, 0, 0, 0.2), 0px 0px 0px 0px rgba(0, 0, 0, 0.14), 0px 0px 0px 0px rgba(0, 0, 0, 0.12) !important
}
</style>
