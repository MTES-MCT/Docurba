<template>
  <v-container>
    <v-row>
      <v-col cols="12">
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
export default {
  data () {
    return {
      loaded: false,
      events: []
    }
  },
  async mounted () {
    const { data: events, error } = await this.$supabase.from('sudocu_events').select('*').eq('noserieprocedure', this.$route.params.duId).eq('codeinseecommune', this.$route.params.collectiviteId.toString().padStart(5, '0'))
    console.log(events, error)
    this.events = events.map((e) => {
      return {
        date_iso: e.dateevenement,
        type: e.libtypeevenement + ' - ' + e.libstatutevenement,
        description: e.commentaire + ' - Document sur le reseau: ' + e.nomdocument,
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
    })
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
