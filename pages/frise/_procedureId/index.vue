<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <!-- <nuxt-link :to="back">
          Retour
        </nuxt-link> -->
        <h1 class="text-h1">
          Feuille de route partagée
        </h1>
        <!-- {{ collectivite }} -->
      </v-col>
    </v-row>
    <v-row v-if="loaded">
      <v-col cols="8">
        <v-card outlined>
          <v-card-text>
            <FriseDocTimeline :events="events" :censored="!isVerified" />
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
</template>

<script>
export default {
  name: 'ProcedureTimelineEvents',
  data () {
    return {
      loaded: false,
      collectivite: null,
      events: []
    }
  },
  computed: {
    back () {
      return {}
      // if (this.$user.id && this.$user.scope && this.$user.scope.dept) {
      //   return { name: 'ddt-departement-collectivites-collectiviteId', params: { departement: $route.params.departement, collectiviteId: $route.params.collectiviteId } }
      // } else {
      //   return { name: 'ddt-departement-collectivites-collectiviteId', params: { departement: $route.params.departement, collectiviteId: $route.params.collectiviteId } }
      // }
    },
    isVerified () {
      return this.$user?.profile?.side === 'etat' && this.$user?.profile?.verified
    }
  },
  async mounted () {
    try {
      if (this.$user && this.$user.isReady) {
        this.$user.isReady.then(() => {
          if (this.isVerified) {
            this.$nuxt.setLayout('ddt')
          }
        })
      }

      await this.getEvents()
      this.loaded = true
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('ERROR: ', error)
    }
  },
  methods: {
    async getEvents () {
      const { data: events, error: errorEvents } = await this.$supabase.from('doc_frise_events').select('*').eq('procedure_id', this.$route.params.procedureId)
      if (errorEvents) { throw errorEvents }
      this.events = events
    }
  }
}
</script>

<style scoped>
.sticky-row {
  position: sticky;
  top: 180px;
}
</style>
