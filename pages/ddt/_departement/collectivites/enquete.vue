<template>
  <v-container>
    <v-row class="pt-6">
      <v-col cols="12">
        <h1 class="text-h1">
          Validation des procédures
        </h1>
      </v-col>
    </v-row>
    <!-- <v-row>
      <v-col cols="12">
        <ProceduresCollectivitiesSearchCard v-model="filteredCollectivities" :collectivities="collectivities" />
      </v-col>
    </v-row> -->
    <v-row v-if="!loading">
      <v-col cols="12">
        <v-card flat tile outlined>
          <v-card-text class="px-5">
            <v-tabs v-model="tab">
              <v-tab>Communes à valider</v-tab>
              <v-tab>Communes validées</v-tab>
              <v-tab>SCOT à valider</v-tab>
              <v-tab>SCOT validés</v-tab>
            </v-tabs>
            <v-tabs-items v-model="tab">
              <v-tab-item>
                <ProceduresCollectivitiesList
                  :collectivities="unvalidatedCollectivities"
                  :intercommunalites="intercommunalites"
                  @validations="updateValidations"
                />
              </v-tab-item>
              <v-tab-item>
                <ProceduresCollectivitiesList
                  :collectivities="validatedCollectivities"
                  :intercommunalites="intercommunalites"
                  validated
                />
              </v-tab-item>
              <v-tab-item>
                <ProceduresScotList :scots="unvalidatedScots" :loaded="scotsLoaded" @validations="updateScotsValidations" />
              </v-tab-item>
              <v-tab-item>
                <ProceduresScotList :scots="validatedScots" :loaded="scotsLoaded" validated />
              </v-tab-item>
            </v-tabs-items>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <VGlobalLoader v-else />
  </v-container>
</template>

<script>
import axios from 'axios'
import { groupBy } from 'lodash'
// import dayjs from 'dayjs'

export default {
  name: 'Enquete',
  layout: 'ddt',
  data () {
    return {
      tab: null,
      collectivities: [],
      scots: [],
      loading: true,
      scotsLoaded: false
    }
  },
  computed: {
    validatedCollectivities () {
      return this.collectivities.filter((c) => {
        return c.validations.length
      })
    },
    unvalidatedCollectivities () {
      return this.collectivities.filter((c) => {
        return !c.validations.length
      })
    },
    unvalidatedScots () {
      return this.scots.filter(s => !s.validations.length)
    },
    validatedScots () {
      return this.scots.filter(s => s.validations.length)
    }
  },
  async mounted () {
    // Fetch communes for departement
    const departementCode = this.$route.params.departement
    const { data: collectivities } = await axios(`/api/geo/communes?departementCode=${departementCode}`)

    this.collectivities = collectivities.map((c) => {
      return Object.assign({
        validations: [],
        procedures: [],
        loaded: false
      }, c)
    })

    const { data: intercommunalites } = await axios(`/api/geo/intercommunalites?departementCode=${departementCode}`)
    this.intercommunalites = intercommunalites

    // TODO: Add a filter to get only last 12 months validations
    const { data: validations } = await this.$supabase.from('procedures_validations').select('*')
      .eq('departement', departementCode)

    this.fetchScots(validations.filter(v => v.doc_type === 'SCOT'))
    this.updateValidations(validations.filter(v => v.doc_type !== 'SCOT'))

    this.loading = false
  },
  methods: {
    async fetchScots (validations) {
      console.log('fetchScots validations', validations)

      // console.log('filteredScots', this.filteredScots)
      const { data: procedures } = await this.$supabase
        .rpc('scot_by_insee_codes', {
          codes: this.collectivities.map(c => c.code)
        })

      // console.log('OPPOSABLE SCOTS', procedures.filter(p => p.status === 'opposable').map(p => `${p.name} - ${p.collectivite_porteuse_id} - ${p.id}`))

      const groupedProcedures = groupBy(procedures, p => p.collectivite_porteuse_id)
      const collectivitiesCodes = Object.keys(groupedProcedures)

      this.scots = collectivitiesCodes.map((collectiviteCode) => {
        return {
          intitule: groupedProcedures[collectiviteCode][0].name,
          code: collectiviteCode,
          procedures: groupedProcedures[collectiviteCode],
          validations: validations.filter(v => v.collectivite_code === collectiviteCode)
        }
      })

      this.scotsLoaded = true
    },
    updateValidations (validations) {
      validations.forEach((validation) => {
        const inseeCode = validation.collectivite_code

        const collectivity = this.collectivities.find(c => c.code === inseeCode)

        if (collectivity) {
          collectivity.validations.push(validation)
        }
      })
    },
    updateScotsValidations (validations) {
      validations.forEach((validation) => {
        const scot = this.scots.find(s => s.code === validation.collectivite_code)
        scot.validations.push(validation)
      })
    }
  }
}
</script>

<style scoped>

</style>
