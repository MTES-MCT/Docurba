import axios from 'axios'
import _ from 'lodash'

export default {
  data () {
    return {
      collectivite: null,
      procedures: null
    }
  },
  computed: {
    isEpci () {
      return this.$route.query.isEpci === true || (this.$route.query.isEpci === 'true')
    }
  },
  async mounted () {
    const { data: collectivite } = await axios({
      url: `/api/${this.isEpci ? 'epci' : 'communes'}/${this.$route.params.collectiviteId}`,
      method: 'get'
    })
    collectivite.name = this.isEpci ? collectivite.label : collectivite.nom_commune
    this.collectivite = collectivite
    console.log('collectivite: ', this.collectivite)
    this.loadCommuneEvents(this.collectivite)
  },
  methods: {
    //     getProcedure(procedureId){
    // this.procedure.filter(e => e.events.)
    //     },
    async loadCommuneEvents (commune) {
      // .eq('codeinseecommune', commune.code_commune_INSEE.toString().padStart(5, '0'))).data
      let codecollectivite
      if (!this.isEpci) {
        codecollectivite = commune.code_commune_INSEE.toString().padStart(5, '0')
      } else { codecollectivite = commune.EPCI }

      const rawEvents = (await this.$supabase.from('sudocu_procedure_events').select().eq('codecollectivite', codecollectivite)).data
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

      const eventsByProc = formattedEvents.reduce(function (r, a) {
        r[a.idProcedure] = r[a.idProcedure] || []
        r[a.idProcedure].push(a)
        return r
      }, Object.create(null))
      console.log('eventsByProc: ', eventsByProc)

      const tempProcs = {}
      for (const [k, v] of Object.entries(eventsByProc)) {
        let procSecs = _.filter(eventsByProc, (e, i) => {
          return e[0].idProcedurePrincipal?.toString() === k
        })

        if (procSecs && procSecs.length > 0) {
          procSecs = procSecs.reduce((acc, curr) => {
            acc[curr[0].idProcedure] = curr
            return acc
          }, {})
        } else { procSecs = null }

        tempProcs[k] = { events: v, procSecs }
      }

      const cleanedProcs = {}
      for (const [k, v] of Object.entries(tempProcs)) {
        if (v.procSecs) { cleanedProcs[k] = v }
      }
      console.log('HERE tempProcs: ', tempProcs)
      console.log('HERE cleanedProcs: ', cleanedProcs)

      function lastStepDate (procedure) {
        if (procedure.events[0].dateAbandon) {
          return procedure.events[0].dateAbandon
        } else if (procedure.events[0].dateExecutoire) {
          return procedure.events[0].dateExecutoire
        } else if (procedure.events[0].dateApprobation) {
          return procedure.events[0].dateApprobation
        } else if (procedure.events[0].dateLancement) {
          return procedure.events[0].dateLancement
        }
        return null
      }

      this.procedures = _.chain(cleanedProcs)
        .map(e => ({
          ...e,
          procSecs: _.chain(e.procSecs)
            .map(i => ({ ...i, lastStepDate: lastStepDate({ events: i }) }))
            .orderBy('lastStepDate', 'desc').value(),
          lastStepDate: lastStepDate(e),
          idProcedure: e.events[0].idProcedure
        }))
        .orderBy('lastStepDate', 'desc').value()

      console.log('eventsByProc after: ', this.procedures)
    }
  }
}
