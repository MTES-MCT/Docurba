<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <p class="text-h2">
          Import des évènements Sudocu
        </p>
        <VTownAutocomplete v-model="selectedTown" />
      </v-col>
      <v-col cols="12">
        <v-btn color="primary" depressed :loading="loading" @click="loadCommuneEvents">
          Visualiser
        </v-btn>
      </v-col>
    </v-row>
    <v-row v-if="!loading && events && docTypes.length === 0">
      <v-col cols="12">
        <div>Pas d'events pour cette commune</div>
      </v-col>
    </v-row>
    <template v-else-if="!loading && events && docTypes.length > 0">
      <v-row>
        <v-col cols="12">
          <v-tabs v-model="selectedDocType">
            <v-tab v-for="docType in docTypes" :key="docType">
              {{ docType }}
            </v-tab>
          </v-tabs>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-tabs v-model="selectedProcedure">
            <v-tab v-for="procedure in procedureIds" :key="'pr_' + procedure">
              {{ procedure }}
            </v-tab>
          </v-tabs>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-alert
            outlined
          >
            <div v-if=" currentEventsProcedure && currentEventsProcedure[0]">
              <div class="text-h6 mb-6">
                {{ currentEventsProcedure[0].typeProcedure }}
              </div>
              <p>
                Rattaché a la pricédure principale: {{ currentEventsProcedure[0].idProcedurePrincipal }}
              </p>
              <p>
                <b>Commentaire DGD: </b> {{ currentEventsProcedure[0].commentaireDgd }}
              </p>
              <p>
                <b>Commentaire Général: </b>  {{ currentEventsProcedure[0].commentaireProcedure }}
              </p>
              <div>
                <div v-if="currentEventsProcedure[0].dateLancement">
                  <b>Date de lancement: </b> {{ currentEventsProcedure[0].dateLancement }}
                </div>
                <div v-if="currentEventsProcedure[0].dateApprobation">
                  <b>Date d'approbation: </b> {{ currentEventsProcedure[0].dateApprobation }}
                </div>
                <div v-if="currentEventsProcedure[0].dateAbandon">
                  <b>Date d'abandon: </b> {{ currentEventsProcedure[0].dateAbandon }}
                </div>
                <div v-if="currentEventsProcedure[0].dateExecutoire">
                  <b>Date executoire: </b>  {{ currentEventsProcedure[0].dateExecutoire }}
                </div>
              </div>
            </div>
          </v-alert>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <FriseDocTimeline :events="currentEventsProcedure" no-project />
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>
<script>
import { groupBy } from 'lodash'

export default {
  name: 'Sudocu',
  data () {
    return {
      selectedTown: null,
      selectedDocType: null,
      selectedProcedure: null,
      loading: false,
      events: null
    }
  },
  computed: {
    docTypes () {
      return Object.keys(this.events)
    },
    procedureIds () {
      return this.eventsByProcedure ? Object.keys(this.eventsByProcedure) : []
    },
    proceduresPrincipales () {
      const princps = groupBy(this.eventsByProcedure, e => e[0].idProcedurePrincipal)
      console.log('princps: ', princps)
      return princps
    },
    currentEventsProcedure () {
      return this.eventsByProcedure[this.procedureIds[this.selectedProcedure]]
    },
    eventsByProcedure () {
      const eventsByProc = this.formatedEvents.reduce(function (r, a) {
        r[a.idProcedure] = r[a.idProcedure] || []
        r[a.idProcedure].push(a)
        return r
      }, Object.create(null))
      console.log('eventsByProc: ', eventsByProc)
      // eventsByProc = eventsByProc[this.procedureIds[this.selectedProcedure]]
      // console.log('procedureIds: ', this.procedureIds)
      return eventsByProc
    },
    formatedEvents () {
      let events = this.events[this.docTypes[this.selectedDocType]]
      const unique = [...new Set(events.map(item => item.idProcedure))]
      console.log('Unique: ', unique)
      const colors = ['pink', 'green', 'blue', 'yellow']
      events = events.map((e) => {
        e.color = colors[unique.indexOf(e.idProcedure)]
        return e
      })
      console.log('toto: ', events)

      return events
    }
  },
  methods: {

    async loadCommuneEvents (commune) {
      const rawEvents = (await this.$supabase.from('sudocu_events').select().eq('codeinseecommune', this.selectedTown.code_commune_INSEE.toString().padStart(5, '0'))).data
      console.log('rawEvents: ', rawEvents)
      const formattedEvents = rawEvents.map((e) => {
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
      this.events = formattedEvents.reduce(function (r, a) {
        r[a.docType] = r[a.docType] || []
        r[a.docType].push(a)
        return r
      }, Object.create(null))

      this.selectedDocType = 0
      console.log('events: ', this.events)
      this.loading = false
    }
  }
}
</script>
