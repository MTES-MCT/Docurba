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
import _ from 'lodash'
export default {
  name: 'ProcedureTimelineEvents',
  layout ({ $user }) {
    // console.log('$user?.profile: ', $user?.profile)
    if ($user?.profile?.side === 'etat' && $user?.profile?.verified) {
      return 'ddt'
    } else {
      return 'default'
    }
  },
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
      const eventsSudocu = await this.$sudocu.getProcedureEvents(this.$route.params.procedureId)

      const { data: procedureDocurba, error: errorProcedureDocurba } = await this.$supabase.from('projects').select('*, doc_frise_events(*)').eq('sudocuh_procedure_id', this.$route.params.procedureId)

      // const { data: procedures, error } = await this.$supabase.from('procedures').select('*')
      //   .eq('is_principale', true)
      //   .contains('current_perimetre', '[{ "inseeCode": "73001" }]')

      if (errorProcedureDocurba) { throw errorProcedureDocurba }
      const eventsDocurba = procedureDocurba?.[0]?.doc_frise_events ?? []

      this.events = _.orderBy(eventsSudocu.map((e) => {
        return {
          from_sudocuh: true,
          date_iso: e.dateevenement,
          type: e.libtypeevenement,
          status: e.libstatutevenement,
          description: '',
          actors: [],
          attachements: e.attachements,
          docType: e.codetypedocument,
          idProcedure: e.noserieprocedure,
          typeProcedure: e.libtypeprocedure,
          idProcedurePrincipal: e.noserieprocedureratt,
          commentaireDgd: e.commentairedgd,
          commentaireProcedure: e.commentaireproc,
          commentaire: e.commentaire,
          dateLancement: e.datelancement,
          dateApprobation: e.dateapprobation,
          dateAbandon: e.dateabandon,
          dateExecutoire: e.dateexecutoire
        }
      }).concat(eventsDocurba), 'date_iso', 'desc')
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
