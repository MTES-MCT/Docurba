<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <nuxt-link :to="{ name: 'ddt-departement-collectivites-collectiviteId', params: { departement: $route.params.departement, collectiviteId: $route.params.collectiviteId }, query: $route.query }">
          Retour
        </nuxt-link>
        <h1 class="text-h1">
          Feuille de route partagée
        </h1>
      </v-col>
    </v-row>
    <v-row v-if="loaded">
      <v-col cols="8">
        <v-card outlined>
          <v-card-text>
            <FriseDocTimeline :events="events" />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="4">
        <v-row class="sticky-row">
          <v-col cols="12">
            <FriseCheckpointsCard :events="events" />
          </v-col>
          <v-col cols="12">
            <FriseLastUpdatesCard :events="events" />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <VGlobalLoader v-else />
  </v-container>
  <!-- <VGlobalLoader v-else /> -->
</template>

<script>
import _ from 'lodash'
export default {
  data () {
    return {
      loaded: false,
      events: []
    }
  },
  async mounted () {
    // const { data: eventsDocruba, error: errorDocurba } = await this.$supabase.from('doc_frise_events').select('*').eq('project_id', this.projectId)
    let eventsSudocu = []
    console.log('(this.$router.query: ', (this.$route.query))
    if (this.$route.query.isEpci === 'true') {
      const { data: eventsSudo, error: errSudoComm } = await this.$supabase.from('sudocu_procedure_events').select('*').eq('noserieprocedure', this.$route.params.procedureId).eq('codecollectivite', this.$route.params.collectiviteId.toString().padStart(5, '0'))
      if (errSudoComm) {
        console.log('Frise errSudoComm: ', errSudoComm)
      }
      eventsSudocu = eventsSudo
    } else {
      const { data: eventsSudo, error: errSudoEpci } = await this.$supabase.from('sudocu_procedure_events').select('*').eq('noserieprocedure', this.$route.params.procedureId).eq('codecollectivite', this.$route.params.collectiviteId)
      if (errSudoEpci) {
        console.log('Frise errSudoEpci: ', errSudoEpci)
      }
      eventsSudocu = eventsSudo
    }

    const { data: procedureDocurba, error: errorProcedureDocurba } = await this.$supabase.from('projects').select('*, doc_frise_events(*)').eq('sudocuh_procedure_id', this.$route.params.procedureId)
    if (errorProcedureDocurba) {
      console.log('Frise errorProcedureDocurba: ', errorProcedureDocurba)
    }
    const eventsDocurba = procedureDocurba?.[0]?.doc_frise_events ?? []
    console.log('events sudo: ', eventsSudocu)
    console.log('procedureDocurba frise: ', procedureDocurba)
    // const { data: procedureDocurba, error: errorProcedureDocurba } = await this.$supabase.from('projects').select('*').eq('sudocuh_procedure_id', this.$route.params.procedureId)
    // if (errorProcedureDocurba) {
    //   console.log('errorProcedureDocurba: ', errorProcedureDocurba)
    // }
    // console.log('procedureDocurba: ', procedureDocurba)
    // const { data, error } = await this.$supabase.from('projects').insert([newProject]).select()

    console.log(eventsSudocu)
    this.events = _.orderBy(eventsSudocu.map((e) => {
      return {
        from_sudocuh: true,
        date_iso: e.dateevenement,
        type: e.libtypeevenement, // + ' - ',  + e.libstatutevenement,
        description: '', // e.commentaire + ' - Document sur le reseau: ' + e.nomdocument,
        actors: [],
        attachements: [],
        docType: e.codetypedocument,
        idProcedure: e.noserieprocedure,
        typeProcedure: e.libtypeprocedure,
        idProcedurePrincipal: e.noserieprocedureratt,
        commentaireDgd: e.commentairedgd,
        commentaireProcedure: e.commentaireproc,
        dateLancement: e.datelancement,
        dateApprobation: e.dateapprobation,
        dateAbandon: e.dateabandon,
        dateExecutoire: e.dateexecutoire
      }
    }).concat(eventsDocurba), 'date_iso', 'desc')
    // this.events = events

    this.loaded = true
  }
}
</script>

<style scoped>
.sticky-row {
  position: sticky;
  top: 180px;
}
</style>
