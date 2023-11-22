<template>
  <v-container>
    <v-row>
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
          <v-card-text>
            <v-tabs v-model="tab">
              <v-tab>Communes à valider</v-tab>
              <v-tab>Communes validées</v-tab>
            </v-tabs>
            <v-tabs-items v-model="tab">
              <v-tab-item>
                <ProceduresCollectivitiesList :collectivities="unvalidatedCollectivities" @validations="updateValidations" />
              </v-tab-item>
              <v-tab-item>
                <ProceduresCollectivitiesList :collectivities="validatedCollectivities" validated @validations="updateValidations" />
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
// import dayjs from 'dayjs'

export default {
  name: 'Enquete',
  layout: 'ddt',
  data () {
    return {
      tab: null,
      collectivities: [],
      loading: true
    }
  },
  computed: {
    validatedCollectivities () {
      console.log('update validated')
      return this.collectivities.filter((c) => {
        return c.validations.length
      })
    },
    unvalidatedCollectivities () {
      return this.collectivities.filter((c) => {
        return !c.validations.length
      })
    }
  },
  async mounted () {
    // Fetch communes for departement
    const departementCode = this.$route.params.departement
    const collectivities = (await axios(`/api/geo/communes?departementCode=${departementCode}`)).data

    const { data: validations } = await this.$supabase.from('procedures_validations').select('*')
    // TODO: Add a filter to get only last 12 months validations

    this.collectivities = collectivities.map((c) => {
      return Object.assign({
        validations: [],
        procedures: [],
        loaded: false
      }, c)
    })

    this.updateValidations(validations)

    this.loading = false
  },
  methods: {
    updateValidations (validations) {
      validations.forEach((validation) => {
        const inseeCode = validation.insee_code

        const collectivity = this.collectivities.find(c => c.code === inseeCode)
        collectivity.validations.push(validation)
      })

      // this.collectivities.validated = this.collectivities.all.filter((c) => {
      //   return c.validations.length
      // })

      // this.collectivities.unvalidated = this.collectivities.all.filter((c) => {
      //   return !c.validations.length
      // })
    }
  }
}
</script>
