<template>
  <v-container v-if="collectivite">
    <v-row>
      <v-col cols="12">
        <h1>{{ collectivite.name }}</h1>
      </v-col>
      <v-col cols="12">
        <v-expansion-panels v-if="isEpci" flat>
          <v-expansion-panel class="beige">
            <v-expansion-panel-header>
              <h3>{{ collectivite.towns.length }} communes dans votre EPCI</h3>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-container>
                <v-row>
                  <v-col
                    v-for="town in collectivite.towns"
                    :key="town.code_commune_INSEE"
                    cols="4"
                    class="pt-0 pl-0"
                  >
                    <nuxt-link :to="{ name: 'dashboard-departement-collectivites-collectiviteId', params: { departement: $route.params.departement, collectiviteId: town.code_commune_INSEE }, query: { isEpci: false } }">
                      {{ town.nom_commune }}
                    </nuxt-link>
                    <v-divider class="mt-3" />
                  </v-col>
                </v-row>
              </v-container>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h2>Documents d'urbanisme</h2>
        <p>
          Documents d’urbanismes disponibles pour la commune recherchée :
        </p>
      </v-col>
      <v-col cols="12">
        <DashboardDUItem
          v-for="(procedure,i) in procedures"
          :key="'du_' + i"
          :procedure="procedure"
        />
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
// import axios from 'axios'
// import _ from 'lodash'
import SudocuEvents from '@/mixins/SudocuEvents.js'

export default {
  mixins: [SudocuEvents]
  // data () {
  //   return {
  //     collectivite: null,
  //     procedures: null
  //   }
  // },
  // computed: {
  //   isEpci () {
  //     return this.$route.query.isEpci === true || (this.$route.query.isEpci === 'true')
  //   }
  // },
  // async mounted () {
  //   const { data: collectivite } = await axios({
  //     url: `/api/${this.isEpci ? 'epci' : 'communes'}/${this.$route.params.collectiviteId}`,
  //     method: 'get'
  //   })
  //   collectivite.name = this.isEpci ? collectivite.label : collectivite.nom_commune
  //   this.collectivite = collectivite
  //   console.log('collectivite: ', this.collectivite)
  //   this.loadCommuneEvents(this.collectivite)
  // },
  // methods: {
  //   async loadCommuneEvents (commune) {
  //     const rawEvents = (await this.$supabase.from('sudocu_events').select().eq('codeinseecommune', commune.code_commune_INSEE.toString().padStart(5, '0'))).data
  //     console.log('rawEvents: ', rawEvents)
  //     const formattedEvents = rawEvents.map((e) => {
  //       return {
  //         date_iso: e.dateevenement,
  //         type: e.libtypeevenement + ' - ' + e.libstatutevenement,
  //         description: e.commentaire + ' - Document sur le reseau: ' + e.nomdocument,
  //         actors: [],
  //         attachements: [],
  //         docType: e.codetypedocument,
  //         idProcedure: e.noserieprocedure,
  //         typeProcedure: e.libtypeprocedure,
  //         idProcedurePrincipal: e.noserieprocedureratt,
  //         commentaireDgd: e.commentairedgd,
  //         commentaireProcedure: e.commentaireproc,
  //         dateLancement: e.datelancement,
  //         dateApprobation: e.dateapprobation,
  //         dateAbandon: e.dateabandon,
  //         dateExecutoire: e.dateexecutoire

  //       }
  //     })

  //     const eventsByProc = formattedEvents.reduce(function (r, a) {
  //       r[a.idProcedure] = r[a.idProcedure] || []
  //       r[a.idProcedure].push(a)
  //       return r
  //     }, Object.create(null))
  //     console.log('eventsByProc: ', eventsByProc)

  //     const tempProcs = {}
  //     for (const [k, v] of Object.entries(eventsByProc)) {
  //       let procSecs = _.filter(eventsByProc, (e, i) => {
  //         return e[0].idProcedurePrincipal?.toString() === k
  //       })

  //       if (procSecs && procSecs.length > 0) {
  //         procSecs = procSecs.reduce((acc, curr) => {
  //           acc[curr[0].idProcedure] = curr
  //           return acc
  //         }, {})
  //       } else { procSecs = null }

  //       tempProcs[k] = { events: v, procSecs }
  //     }

  //     const cleanedProcs = {}
  //     for (const [k, v] of Object.entries(tempProcs)) {
  //       if (v.procSecs) { cleanedProcs[k] = v }
  //     }
  //     console.log('HERE tempProcs: ', tempProcs)
  //     console.log('HERE cleanedProcs: ', cleanedProcs)

  //     function lastStepDate (procedure) {
  //       if (procedure.events[0].dateAbandon) {
  //         return procedure.events[0].dateAbandon
  //       } else if (procedure.events[0].dateExecutoire) {
  //         return procedure.events[0].dateExecutoire
  //       } else if (procedure.events[0].dateApprobation) {
  //         return procedure.events[0].dateApprobation
  //       } else if (procedure.events[0].dateLancement) {
  //         return procedure.events[0].dateLancement
  //       }
  //       return null
  //     }

  //     this.procedures = _.chain(cleanedProcs).map(e => ({ ...e, procSecs: _.chain(e.procSecs).map(i => ({ ...i, lastStepDate: lastStepDate({ events: i }) })).orderBy('lastStepDate', 'desc').value(), lastStepDate: lastStepDate(e) })).orderBy('lastStepDate', 'desc').value()

  //     console.log('eventsByProc after: ', this.procedures)
  //   }
  // }
}
</script>
