<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="text-h1">
          Liste des communes concernées
        </div>
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <!-- <nuxt-link
            :to="{ name: `ddt-departement-collectivites-collectiviteId-${$sudocu.isEpci($route.params.collectiviteId) ? 'epci' : 'commune'}`, params: { departement: $route.params.departement, collectiviteId: $route.params.collectiviteId }}"
          >
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span>Revenir à mon tableau de bord</span>
          </nuxt-link> -->
        </div>
      </v-col>
    </v-row>
    <DashboardDdtInfosTabs />
    <v-row v-if="procedure" class="white">
      <v-col
        v-for="town in procedure.procedures_perimetres"
        :key="town.code + town.collectivite_type"
        cols="4"
      >
        <nuxt-link :to="{ name: 'ddt-departement-collectivites-collectiviteId-commune', params: { departement: $route.params.departement, collectiviteId: town.code }, query: { isEpci: false } }">
          {{ town.intitule }} ({{ town.code }} {{ town.collectivite_type }})
        </nuxt-link>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'InformationsGenerales',
  layout: 'ddt',
  data () {
    return {
      procedure: null
    }
  },
  async mounted () {
    const { data: procedures, error: errorProcedure } = await this.$supabase.from('procedures')
      .select('*')
      .eq('id', this.$route.params.procedureId)
    if (errorProcedure) { throw errorProcedure }

    const parsedProcedures = await this.$urbanisator.getProceduresPerimetre(procedures, this.$route.params.collectiviteId)
    this.procedure = parsedProcedures[0]

    console.log(this.procedure)
  }
}
</script>
