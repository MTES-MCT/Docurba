<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          Validation des procédures
        </h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <ProceduresCollectivitiesSearchCard v-model="filteredCollectivities" :collectivities="collectivities" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <ProceduresCollectivitiesList :collectivities="filteredCollectivities" />
      </v-col>
      <v-col cols="4">
        <v-pagination v-model="page" :length="Math.ceil(collectivities.length/10)" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Enquete',
  layout: 'ddt',
  data () {
    return {
      collectivities: [],
      page: 1
    }
  },
  computed: {
    filteredCollectivities () {
      const pageIndex = (this.page - 1) * 10
      return this.collectivities.slice(pageIndex, pageIndex + 10)
    }
  },
  watch: {
    page () {
      this.fetchCollectivitiesProcedures()
    }
  },
  async mounted () {
    // Fetch communes for departement
    const departementCode = this.$route.params.departement
    const collectivities = (await axios(`/api/geo/communes?departementCode=${departementCode}`)).data

    this.collectivities = collectivities.map((c) => {
      return Object.assign({ procedures: [] }, c)
    })

    this.fetchCollectivitiesProcedures()
  },
  methods: {
    fetchCollectivitiesProcedures () {
      console.log('filteredCollectivities', this.filteredCollectivities)

      this.filteredCollectivities.forEach(async (collectivite) => {
        // console.log(collectivite.procedures, !collectivite.procedures.length)
        if (!collectivite.procedures.length) {
          const inseeCode = collectivite.code

          const { data: procedures } = await this.$supabase.from('procedures')
            .select('id, status, doc_type, current_perimetre, is_pluih')
            .contains('current_perimetre', `[{ "inseeCode": "${inseeCode}" }]`)
            .in('status', ['opposable', 'en cour'])
            .eq('is_principale', true)

          procedures.forEach((procedure) => {
            if (procedure.doc_type === 'PLU' && procedure.current_perimetre.length > 1) {
              procedure.doc_type += 'i'

              if (procedure.is_pluih) {
                procedure.doc_type += 'h'
              }
            }
          })

          collectivite.procedures = procedures
        }
      })
    }
  }
}
</script>
