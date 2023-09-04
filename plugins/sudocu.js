import _ from 'lodash'

// const { data: rawEvents, error: rawEventsError, ...args } = await this.$supabase.from('sudocu_procedure_events').select('*', { count: 'exact' }).eq('codecollectivite', codecollectivite)
// console.log('args: ', args)
// if (rawEventsError) { throw rawEventsError }

function parseAttachment (path) {
  if (path) {
    const attachment = { id: '', name: '', type: 'file' }
    let temp = ''
    const semiSplit = path.split(':')
    if (semiSplit[0] === 'link') { attachment.type = 'link' }
    semiSplit.length > 1 ? temp = semiSplit[1] : temp = semiSplit[0]
    attachment.name = temp
    attachment.id = 'sudocu/' + temp.split('_').slice(1).join('/')
    return [attachment]
  } else {
    return []
  }
}

function formatSudocuProcedure (rawProcedures) {
  return rawProcedures.map((e) => {
    return {
      // This keys are only for backward comatibility but should not be used.
      // Use new keys below that match procedure table in bdd.
      date_iso: e.last_event_date,
      // type: e.libtypeevenement + ' - ' + e.last_event_statut, // Maybe we dont need this.
      // description: e.commentaire + ' - Document sur le reseau: ' + e.nomdocument,
      actors: [],
      attachements: [],
      docType: e.codetypedocument,
      idProcedure: e.noserieprocedure || e.id_procedure,
      name: e.nomschema,
      typeProcedure: e.libtypeprocedure,
      idProcedurePrincipal: e.noserieprocedureratt,
      commentaireDgd: e.commentairedgd, // This should be kep always for historic data
      commentaireProcedure: e.commentaireproc, // This should be kep always for historic data
      dateLancement: e.datelancement,
      dateApprobation: e.dateapprobation,
      dateAbandon: e.dateabandon,
      dateExecutoire: e.dateexecutoire,
      // new keys from procedure table on supabase
      id: e.noserieprocedure || e.id_procedure,
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
}

export default ({ route, store, $supabase, $urbanisator }, inject) => {
  inject('sudocu', {
    async getProcedureInfosDgd (procedureId) {
      try {
        if (typeof procedureId === 'string') { procedureId = parseInt(procedureId) }
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

        const rawPlanEvents = await $supabase.from('sudocu_procedure_events').select('*').eq('noserieprocedure', procedureId)
        const rawSchemaEvents = await $supabase.from('sudocu_schemas_events').select('*').eq('noserieprocedure', procedureId)
        const [{ data: planEvents, error: errPlanEvents }, { data: schemaEvents, error: errSchemaEvents }] = await Promise.all([rawPlanEvents, rawSchemaEvents])
        if (errPlanEvents) { throw new Error(errPlanEvents) }
        if (errSchemaEvents) { throw new Error(errSchemaEvents) }

        const formattedEvs = planEvents.map(e => ({ ...e, attachements: parseAttachment(e.nomdocument) }))

        return formattedEvs.concat(schemaEvents)
      } catch (error) {
        console.log('ERROR getProcedureEvents:', error)
      }
    },
    async getProceduresEvents (arrProceduresId) {
      try {
        // TODO: Re rajouter les SCOT proprement
        const rawPlanEvents = await $supabase.from('sudocu_procedure_events').select('*').in('noserieprocedure', arrProceduresId)
        const rawSchemaEvents = await $supabase.from('sudocu_schemas_events').select('*').in('noserieprocedure', arrProceduresId)
        const [{ data: planEvents, error: errPlanEvents }, { data: schemaEvents, error: errSchemaEvents }] = await Promise.all([rawPlanEvents, rawSchemaEvents])
        if (errPlanEvents) { throw new Error(errPlanEvents) }
        if (errSchemaEvents) { throw new Error(errSchemaEvents) }

        const formattedEvs = planEvents.map(e => ({ ...e, attachements: parseAttachment(e.nomdocument) }))
        const allEvts = formattedEvs.concat(schemaEvents)
        return _.groupBy(allEvts, e => e.noserieprocedure)
      } catch (error) {
        console.log('ERROR getProcedureEvents:', error)
      }
    },
    async getProceduresCollectivite (collectiviteId) {
      // TODO: Ne gere que le PLAN pour le moment, il faut ajouter le SCOT
      // On recupère les périmètres des procédures de la commune. Si c'est une EPCI on filtre sur la collectivite porteuse
      const proceduresCollecQuery = $supabase.from('sudocu_procedures_perimetres').select('*')
      collectiviteId = collectiviteId.toString().padStart(5, '0')

      let proceduresCollec = null
      if (collectiviteId > 5) {
        proceduresCollec = await proceduresCollecQuery.eq('code_collectivite_porteuse', collectiviteId)
      } else {
        proceduresCollec = await proceduresCollecQuery.contains('communes_insee', [collectiviteId])
      }
      console.log('TEST proceduresCollec: ', proceduresCollec)
      // On fetch les procédures faisant parti du périmètre de la commune
      const proceduresCollecIds = proceduresCollec.data.map(e => e.procedure_id)
      const rawPlanProcedures = await $supabase.from('distinct_procedures_events').select('*').in('noserieprocedure', proceduresCollecIds)

      const planProcedures = rawPlanProcedures.data.map((rawPlanProcedure) => {
        const collectivitePorteuse = proceduresCollec.data.find(e => e.procedure_id === rawPlanProcedure.noserieprocedure)
        return { ...rawPlanProcedure, nbCommunesPerimetre: collectivitePorteuse.nb_communes, collectivitePorteuse: _.pick(collectivitePorteuse, ['code_collectivite_porteuse', 'type_collectivite_porteuse']) }
      })
      console.log('TEST planProcedures: ', planProcedures)
      // TODO: On fetch tous les events liées aux procédures
      const allProceduresEvents = await this.getProceduresEvents(proceduresCollecIds)
      console.log('EVENTS OF EACH PROCEDURES: ', allProceduresEvents)
      const planProceduresEvents = planProcedures.map(procedure => ({ ...procedure, events: allProceduresEvents[procedure.noserieprocedure] }))
      console.log('TEST planProceduresEvents: ', planProceduresEvents)
      return planProceduresEvents
    },
    async getProcedures (communeId) {
      try {
        let codecollectivite
        if ($urbanisator.isEpci(communeId)) {
          codecollectivite = communeId
        } else {
          codecollectivite = communeId.toString().padStart(5, '0')
        }

        const promPlanProcedures = await $supabase.from('distinct_procedures_events').select('*').eq('codecollectivite', codecollectivite)
        const promSchemaProcedures = await $supabase.from('distinct_procedures_schema_events').select('*').eq('codecollectivite', codecollectivite).order('last_event_date', { ascending: true })

        const [{ data: rawPlanProcedures, error: rawProceduresError }, { data: rawSchemaProcedures, error: rawSchemaProceduresError }] = await Promise.all([promPlanProcedures, promSchemaProcedures])
        if (rawProceduresError) { throw rawProceduresError }
        if (rawSchemaProceduresError) { throw rawSchemaProceduresError }
        const rawProcedures = rawPlanProcedures.concat(rawSchemaProcedures)

        const formattedProcedures = formatSudocuProcedure(rawProcedures)
        const allProceduresEnriched = await this.loadPerimetre(formattedProcedures)

        const typePrincipalProcedures = ['Elaboration', 'Révision', 'Abrogation', 'Engagement', 'Réengagement']
        const [procsPrincipales, procsSecondaires] = _.partition(allProceduresEnriched, procedure => typePrincipalProcedures.includes(procedure.typeProcedure))

        const groupedProcsSecondaires = _.groupBy(procsSecondaires, e => e.idProcedurePrincipal?.toString())
        const fullProcs = _.map(procsPrincipales, (procedurePrincipale) => {
          procedurePrincipale.procSecs = groupedProcsSecondaires[procedurePrincipale.idProcedure]
          return procedurePrincipale
        })
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
