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
            <FriseCheckpoints :events="events" />
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
      projectId: this.$route.params.projectId,
      events: []
    }
  },
  async mounted () {
    const { data: events } = await this.$supabase.from('doc_frise_events').select('*').eq('project_id', this.projectId)
    this.events = events

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
