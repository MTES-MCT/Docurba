import _ from 'lodash'

// const { data: rawEvents, error: rawEventsError, ...args } = await this.$supabase.from('sudocu_procedure_events').select('*', { count: 'exact' }).eq('codecollectivite', codecollectivite)
// console.log('args: ', args)
// if (rawEventsError) { throw rawEventsError }

export default ({ route, store, $supabase, $urbanisator }, inject) => {
  inject('sudocu', {
    async getProcedureInfosDgd (procedureId) {
      try {
        if (typeof procedureId === 'string') { procedureId = parseInt(procedureId) }
        console.log('procedureId: ', procedureId)
        const { data: rawDetailsProcedure, error: rawDetailsProcedureError } = await $supabase.from('sudocu_procedures_infosdgd').select('*').eq('procedure_id', procedureId)
        if (rawDetailsProcedureError) { throw rawDetailsProcedureError }
        return rawDetailsProcedure
      } catch (error) {
        console.log('ERROR getProcedureInfosDgd: ', error)
      }
    },
    async getProcedureEvents (procedureId) {
      try {
        if (typeof procedureId === 'string') { procedureId = parseInt(procedureId) }
        const { data: events, error: errEvents } = await $supabase.from('sudocu_procedure_events').select('*').eq('noserieprocedure', procedureId)
        if (errEvents) {
          console.log('Frise errEvents: ', errEvents)
          throw new Error(errEvents)
        }
        return events
      } catch (error) {
        console.log('ERROR getProcedureEvents:', error)
      }
    },

    async getProcedures (communeId) {
      try {
        let codecollectivite
        if ($urbanisator.isEpci(communeId)) {
          codecollectivite = communeId
        } else {
          codecollectivite = communeId.toString().padStart(5, '0')
        }

        const { data: rawProcedures, error: rawProceduresError } = await $supabase.from('distinct_procedures_events').select('*').eq('codecollectivite', codecollectivite)
        if (rawProceduresError) { throw rawProceduresError }
        const formattedProcedures = rawProcedures.map((e) => {
          return {
            // This keys are only for backward comatibility but should not be used.
            // Use new keys below that match procedure table in bdd.
            date_iso: e.last_event_date,
            // type: e.libtypeevenement + ' - ' + e.last_event_statut, // Maybe we dont need this.
            // description: e.commentaire + ' - Document sur le reseau: ' + e.nomdocument,
            actors: [],
            attachements: [],
            docType: e.codetypedocument,
            idProcedure: e.noserieprocedure,
            typeProcedure: e.libtypeprocedure,
            idProcedurePrincipal: e.noserieprocedureratt,
            commentaireDgd: e.commentairedgd, // This should be kep always for historic data
            commentaireProcedure: e.commentaireproc, // This should be kep always for historic data
            dateLancement: e.datelancement,
            dateApprobation: e.dateapprobation,
            dateAbandon: e.dateabandon,
            dateExecutoire: e.dateexecutoire,

            // new keys from procedure table on supabase
            id: e.noserieprocedure,
            type: e.libtypeprocedure,
            description: e.commentaire + ' - Document sur le reseau: ' + e.nomdocument,
            procedure_id: e.noserieprocedureratt,
            launch_date: e.datelancement,
            approval_date: e.dateapprobation, // Probably need to parse date to correct format.
            abort_date: e.dateabandon, // Probably need to parse date to correct format.
            enforceable_date: e.dateexecutoire, // Probably need to parse date to correct format.
            created_at: e.datelancement, // Probably need to parse date to correct format.
            last_updated_at: e.last_event_date // Probably need to parse date to correct format.
          }
        })
        const allProceduresEnriched = await this.loadPerimetre(formattedProcedures)

        const typePrincipalProcedures = ['Elaboration', 'Révision', 'Abrogation', 'Engagement', 'Réengagement']
        const [procsPrincipales, procsSecondaires] = _.partition(allProceduresEnriched, procedure => typePrincipalProcedures.includes(procedure.typeProcedure))

        const groupedProcsSecondaires = _.groupBy(procsSecondaires, e => e.idProcedurePrincipal?.toString())
        const fullProcs = _.map(procsPrincipales, (procedurePrincipale) => {
          procedurePrincipale.procSecs = groupedProcsSecondaires[procedurePrincipale.idProcedure]
          return procedurePrincipale
        })
        console.log('fullProcs: ', fullProcs, fullProcs.find(p => p.docType === 'PLUi'))
        return fullProcs
      } catch (error) {
        console.log('Error: ', error)
      }
    },
    async loadPerimetre (procedures) {
      try {
        const proceduresIds = procedures.map(procedure => procedure.idProcedure)
        const {
          data: allPerim,
          error: allPerimError
        } = await $supabase.from('sudocu_procedures_perimetres').select().in('procedure_id', proceduresIds)
        if (allPerimError) { throw allPerimError }

        const {
          data: ongoingProceduresStates,
          error: ongoingProceduresStatesError
        } = await $supabase.from('sudocu_procedures_etats').select().in('id_procedure_ongoing', proceduresIds)
        if (ongoingProceduresStatesError) { throw ongoingProceduresStatesError }

        const {
          data: approvedProceduresStates,
          error: approvedProceduresStatesError
        } = await $supabase.from('sudocu_procedures_etats').select().in('id_procedure_approved', proceduresIds)
        if (approvedProceduresStatesError) { throw approvedProceduresStatesError }

        const proceduresEnrich = procedures.map((procedure) => {
          procedure.approvedInTowns = []
          procedure.ongoingInTowns = []

          const approvedInTowns = approvedProceduresStates.filter(i => i.id_procedure_approved === procedure.idProcedure)
          if (approvedInTowns.length > 0) {
            procedure.approvedInTowns = approvedInTowns.map(i => i.insee_code)
          }

          const ongoingInTowns = ongoingProceduresStates.filter(i => i.id_procedure_ongoing === procedure.idProcedure)
          if (ongoingInTowns.length > 0) {
            procedure.ongoingInTowns = ongoingInTowns.map(i => i.insee_code)
          }

          const collecPerim = allPerim.find(i => i.procedure_id === procedure.idProcedure)
          procedure.perimetre = collecPerim.communes_insee.reduce((acc, curr, idx) => {
            acc.push({ inseeCode: collecPerim.communes_insee[idx], name: collecPerim.name_communes[idx] })
            return acc
          }, [])

          // This is to simulate a join on project_id in procedure table
          const isEpci = procedure.perimetre.length > 1

          procedure.project = {
            towns: procedure.perimetre,
            doc_type: (procedure.docType === 'PLU' && isEpci) ? 'PLUi' : procedure.docType
          }

          return procedure
        })
        return proceduresEnrich
      } catch (error) {
        console.log('ERROR - [loadPerimetre]: ', error)
      }
    }
  })
}
