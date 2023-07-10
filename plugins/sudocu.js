import axios from 'axios'
import _ from 'lodash'

// const { data: rawEvents, error: rawEventsError, ...args } = await this.$supabase.from('sudocu_procedure_events').select('*', { count: 'exact' }).eq('codecollectivite', codecollectivite)
// console.log('args: ', args)
// if (rawEventsError) { throw rawEventsError }

export default ({ route, store, $supabase }, inject) => {
  inject('sudocu', {
    isEpci (collectiviteId) {
      return collectiviteId.toString().length > 5
    },
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
    async getCurrentCollectivite (collectiviteId) {
      try {
        const { data: collectivite } = await axios({
          url: `/api/${this.isEpci(collectiviteId) ? 'epci' : 'communes'}/${collectiviteId}`,
          method: 'get'
        })
        collectivite.name = this.isEpci(collectiviteId) ? collectivite.label : collectivite.nom_commune
        collectivite.type = this.isEpci(collectiviteId) ? 'epci' : 'commune'
        return collectivite
      } catch (error) {
        console.log('Error getCurrentCollectivite: ', error)
      }
    },
    async getProcedures (communeId) {
      try {
        let codecollectivite
        if (this.isEpci(communeId)) {
          codecollectivite = communeId
        } else {
          codecollectivite = communeId.toString().padStart(5, '0')
        }

        const { data: rawProcedures, error: rawProceduresError } = await $supabase.from('distinct_procedures_events').select('*').eq('codecollectivite', codecollectivite)
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
          procedurePrincipale.procSecs = groupedProcsSecondaires[procedurePrincipale.idProcedure]
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
        const { data: allPerim, error: allPerimError } = await $supabase.from('sudocu_procedures_perimetres').select().in('procedure_id', proceduresIds)
        if (allPerimError) { throw allPerimError }
        const { data: ongoingProceduresStates, error: ongoingProceduresStatesError } = await $supabase.from('sudocu_procedures_etats').select().in('id_procedure_ongoing', proceduresIds)
        if (ongoingProceduresStatesError) { throw ongoingProceduresStatesError }
        const { data: approvedProceduresStates, error: approvedProceduresStatesError } = await $supabase.from('sudocu_procedures_etats').select().in('id_procedure_approved', proceduresIds)
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
  })
}
