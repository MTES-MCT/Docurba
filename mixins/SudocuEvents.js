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
    routeIsEpci () {
      return this.$route.query.isEpci === true || (this.$route.query.isEpci === 'true')
    }
  },
  async mounted () {
    this.collectivite = await this.getCurrentCollectivite()
    this.procedures = await this.getProcedures(this.collectivite)
  },
  methods: {
    async getCurrentCollectivite () {
      const { data: collectivite } = await axios({
        url: `/api/${this.routeIsEpci ? 'epci' : 'communes'}/${this.$route.params.collectiviteId}`,
        method: 'get'
      })
      collectivite.name = this.routeIsEpci ? collectivite.label : collectivite.nom_commune
      return collectivite
    },
    async getProcedures (commune) {
      try {
        let codecollectivite
        if (!this.routeIsEpci) {
          console.log('commune: ', commune)
          codecollectivite = commune.code_commune_INSEE.toString().padStart(5, '0')
        } else { codecollectivite = commune.EPCI }
        const { data: rawProcedures, error: rawProceduresError } = await this.$supabase.from('distinct_procedures_events').select('*').eq('codecollectivite', codecollectivite)
        if (rawProceduresError) { throw rawProceduresError }
        const formattedProcedures = rawProcedures.map((e) => {
          return {
            date_iso: e.last_event_date,
            type: e.libtypeevenement + ' - ' + e.last_event_statut,
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
        const allProceduresEnriched = await this.loadPerimetre(formattedProcedures)

        const typePrincipalProcedures = ['Elaboration', 'Révision', 'Abrogation', 'Engagement', 'Réengagement']
        const [procsPrincipales, procsSecondaires] = _.partition(allProceduresEnriched, procedure => typePrincipalProcedures.includes(procedure.typeProcedure))

        const groupedProcsSecondaires = _.groupBy(procsSecondaires, e => e.idProcedurePrincipal?.toString())
        const fullProcs = _.map(procsPrincipales, (procedurePrincipale) => {
          procedurePrincipale.procSecs = groupedProcsSecondaires[procedurePrincipale.idProcedurePrincipal]
          return procedurePrincipale
        })
        console.log('fullProcs: ', fullProcs)
        return fullProcs
      } catch (error) {
        console.log('Error: ', error)
      }
    },

    async loadPerimetre (procedures) {
      try {
        const proceduresIds = procedures.map(e => e.idProcedure)
        const { data: allPerim, error: allPerimError } = await this.$supabase.from('sudocu_procedures_perimetres').select().in('procedure_id', proceduresIds)
        if (allPerimError) { throw allPerimError }
        const { data: ongoingProceduresStates, error: ongoingProceduresStatesError } = await this.$supabase.from('sudocu_procedures_etats').select().in('id_procedure_ongoing', proceduresIds)
        if (ongoingProceduresStatesError) { throw ongoingProceduresStatesError }
        const { data: approvedProceduresStates, error: approvedProceduresStatesError } = await this.$supabase.from('sudocu_procedures_etats').select().in('id_procedure_approved', proceduresIds)
        if (approvedProceduresStatesError) { throw approvedProceduresStatesError }
        const proceduresEnrich = procedures.map((e) => {
          e.approvedInTowns = []
          e.ongoingInTowns = []
          const approvedInTowns = approvedProceduresStates.filter(i => i.id_procedure_approved === e.idProcedure)
          if (approvedInTowns.length > 0) {
            e.approvedInTowns = approvedInTowns.map(i => i.insee_code)
          }

          const ongoingInTowns = ongoingProceduresStates.filter(i => i.id_procedure_ongoing === e.idProcedure)
          if (ongoingInTowns.length > 0) {
            e.ongoingInTowns = ongoingInTowns.map(i => i.insee_code)
          }

          const collecPerim = allPerim.find(i => i.procedure_id === e.idProcedure)
          e.perimetre = collecPerim.communes_insee.reduce((acc, curr, idx) => {
            acc.push({ inseeCode: collecPerim.communes_insee[idx], name: collecPerim.name_communes[idx] })
            return acc
          }, [])
          return e
        })
        return proceduresEnrich
      } catch (error) {
        console.log('ERROR - [loadPerimetre]: ', error)
      }
    },
    async loadCommuneEvents (commune) {
      try {
        let codecollectivite
        if (!this.routeIsEpci) {
          codecollectivite = commune.code_commune_INSEE.toString().padStart(5, '0')
        } else { codecollectivite = commune.EPCI }
        const { data: rawEvents, error: rawEventsError, ...args } = await this.$supabase.from('sudocu_procedure_events').select('*', { count: 'exact' }).eq('codecollectivite', codecollectivite)
        console.log('args: ', args)
        if (rawEventsError) { throw rawEventsError }
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
        console.log('formattedEvents: ', formattedEvents.length)
        const typePrincipalProcedures = ['Elaboration', 'Révision', 'Abrogation', 'Engagement', 'Réengagement']
        // const eventsByProc = formattedEvents.reduce(function (r, a) {
        //   r[a.idProcedure] = r[a.idProcedure] || []
        //   r[a.idProcedure].push(a)
        //   return r
        // }, {})
        const eventsByProc = _.groupBy(formattedEvents, (formattedEvent) => {
          return formattedEvent.idProcedure
        })

        console.log('eventsByProc', Object.keys(eventsByProc).length)
        const tempProcs = {}
        for (const [k, v] of Object.entries(eventsByProc)) {
          let procSecs = _.filter(eventsByProc, (e, i) => {
            return e[0].idProcedurePrincipal?.toString() === k && !typePrincipalProcedures.includes(e[0].typeProcedure)
          })

          if (procSecs && procSecs.length > 0) {
            procSecs = procSecs.reduce((acc, curr) => {
              acc[curr[0].idProcedure] = curr
              return acc
            }, {})
          } else { procSecs = null }
          if (typePrincipalProcedures.includes(v[0].typeProcedure)) {
            tempProcs[k] = { type: v[0].typeProcedure, events: v, procSecs }
          }
        }
        const cleanedProcs = tempProcs
        console.log('cleanedProcs: ', Object.keys(cleanedProcs).length)
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

        const procedures = _.chain(cleanedProcs)
          .map(e => ({
            ...e,
            procSecs: _.chain(e.procSecs)
              .map(i => ({ ...i, lastStepDate: lastStepDate({ events: i }) }))
              .orderBy('lastStepDate', 'desc').value(),
            lastStepDate: lastStepDate(e),
            idProcedure: e.events[0].idProcedure
          }))
          .orderBy('lastStepDate', 'desc').value()

        // this.procedures = await this.loadPerimetre(procedures)

        console.log('BEFORE perimetersProcedures: ', procedures)
        const loadPerimetre = async (procedures) => {
          try {
            const proceduresIds = procedures.map(e => e.idProcedure)
            const { data: allPerim, error: allPerimError } = await this.$supabase.from('sudocu_procedures_perimetres').select().in('procedure_id', proceduresIds)
            if (allPerimError) { throw allPerimError }
            const { data: ongoingProceduresStates, error: ongoingProceduresStatesError } = await this.$supabase.from('sudocu_procedures_etats').select().in('id_procedure_ongoing', proceduresIds)
            if (ongoingProceduresStatesError) { throw ongoingProceduresStatesError }
            const { data: approvedProceduresStates, error: approvedProceduresStatesError } = await this.$supabase.from('sudocu_procedures_etats').select().in('id_procedure_approved', proceduresIds)
            if (approvedProceduresStatesError) { throw approvedProceduresStatesError }
            const proceduresEnrich = procedures.map((e) => {
              e.approvedInTowns = []
              e.ongoingInTowns = []
              const approvedInTowns = approvedProceduresStates.filter(i => i.id_procedure_approved === e.idProcedure)
              if (approvedInTowns.length > 0) {
                e.approvedInTowns = approvedInTowns.map(i => i.insee_code)
              }

              const ongoingInTowns = ongoingProceduresStates.filter(i => i.id_procedure_ongoing === e.idProcedure)
              if (ongoingInTowns.length > 0) {
                e.ongoingInTowns = ongoingInTowns.map(i => i.insee_code)
              }

              const collecPerim = allPerim.find(i => i.procedure_id === e.idProcedure)
              e.perimetre = collecPerim.communes_insee.reduce((acc, curr, idx) => {
                acc.push({ inseeCode: collecPerim.communes_insee[idx], name: collecPerim.name_communes[idx] })
                return acc
              }, [])
              return e
            })
            return proceduresEnrich
          } catch (error) {
            console.log('ERROR - [loadPerimetre]: ', error)
          }
        }

        const perimetersProcedures = await loadPerimetre(procedures)
        console.log('perimetersProcedures: ', perimetersProcedures)
        return perimetersProcedures
      } catch (error) {
        console.log('ERROR - [loadCommuneEvents]: ', error)
      }
    }
  }
}
