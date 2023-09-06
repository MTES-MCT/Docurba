import _ from 'lodash'
import axios from 'axios'
// import epcisList from ('./Data/EPCI.json')
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
        const rawPlanEvents = await $supabase.from('sudocu_procedure_events').select('*').in('noserieprocedure', arrProceduresId).order('dateevenement', { ascending: true })
        const rawSchemaEvents = await $supabase.from('sudocu_schemas_events').select('*').in('noserieprocedure', arrProceduresId).order('dateevenement', { ascending: true })
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
      // TODO: Refaire un export avec le name_collectivite_porteuse (erreur ici on a le type de la collec a la place)
      // TODO: Refaire l'import des events avec le code event plutot que uniquement le label

      // On recupère les périmètres des procédures de la commune. Si c'est une EPCI on filtre sur la collectivite porteuse
      const proceduresCollecQuery = $supabase.from('sudocu_procedures_perimetres').select('*')
      collectiviteId = collectiviteId.toString().padStart(5, '0')

      let proceduresCollec = null
      if (collectiviteId.length > 5) {
        console.log('Searching procédures for epci: ', collectiviteId)
        proceduresCollec = await proceduresCollecQuery.eq('code_collectivite_porteuse', collectiviteId)
      } else {
        console.log('Searching procédures for commune: ', [collectiviteId])
        proceduresCollec = await proceduresCollecQuery.contains('communes_insee', [collectiviteId])
      }
      const proceduresCollecIds = proceduresCollec.data.map(e => e.procedure_id)

      // On fetch les procédures faisant parti du périmètre de la commune
      const rawPlanProcedures = await $supabase.from('distinct_procedures_events').select('*').in('noserieprocedure', proceduresCollecIds).order('last_event_date', { ascending: true })
      console.log('TEST rawPlanProcedures: ', rawPlanProcedures)

      // On fetch tous les events liées aux procédures
      const allProceduresEvents = await this.getProceduresEvents(proceduresCollecIds)
      console.log('EVENTS OF EACH PROCEDURES: ', allProceduresEvents)

      // Fetch des EPCIs porteuses des différentes procédures
      let epcisPorteuses = []
      const collecPorteusesIds = [...new Set(proceduresCollec.data.filter(e => e.type_collectivite_porteuse !== 'COM').map(e => e.code_collectivite_porteuse))]
      if (collecPorteusesIds.length > 0) {
        console.log('LIST IDS EPCI PORTEUSES: ', collecPorteusesIds)
        epcisPorteuses = (await axios({ url: '/api/geo/intercommunalites', method: 'get', params: { codes: collecPorteusesIds } })).data

        console.log('EPCI PORTEUSES: ', epcisPorteuses)
      }
      let communesPorteuses = []
      const communesPorteusesIds = [...new Set(proceduresCollec.data.filter(e => e.type_collectivite_porteuse === 'COM').map(e => e.code_collectivite_porteuse))]
      if (communesPorteusesIds.length > 0) {
        console.log('LIST IDS COMMUNES PORTEUSES: ', communesPorteusesIds)
        communesPorteuses = (await axios({
          url: '/api/geo/communes',
          method: 'get',
          params: { codes: communesPorteusesIds }
        })).data

        console.log('COMMUNES PORTEUSES: ', communesPorteuses)
      }
      // TODO utiliser ca
      const collectivitesPorteuses = epcisPorteuses.concat(communesPorteuses)
      console.log('collectivitesPorteuses: ', collectivitesPorteuses)
      // Raccordement des events à leur procédure
      const planProceduresEvents = rawPlanProcedures.data.map(procedure => ({ ...procedure, events: allProceduresEvents[procedure.noserieprocedure] }))
      console.log('TEST planProceduresEvents: ', planProceduresEvents)

      const planProcedures = planProceduresEvents.map((rawPlanProcedure, idx) => {
        // Raccordements des périmètres aux procédures
        const collecPerim = proceduresCollec.data.find(i => i.procedure_id === rawPlanProcedure.noserieprocedure)
        rawPlanProcedure.perimetre = collecPerim.communes_insee.reduce((acc, curr, idx) => {
          acc.push({ inseeCode: collecPerim.communes_insee[idx], name: collecPerim.name_communes[idx] })
          return acc
        }, [])
        // Enrichissement des collectivités porteuses de chaque procédures
        const collectivitePorteuse = proceduresCollec.data.find(e => e.procedure_id === rawPlanProcedure.noserieprocedure)

        let statusProcedure = 'inconnu'
        let statusInfos = {}

        // Vérification de la sectorialité - si le périmètre de la procédure est plus petit que la collectivité porteuse
        const fullDetailsCollecPorteuse = collectivitesPorteuses.find(e => e.code === collectivitePorteuse.code_collectivite_porteuse)
        console.log('FULL DETAILS COLLEC PORTEUSE: ', fullDetailsCollecPorteuse, ' FOR: ', collectivitePorteuse.code_collectivite_porteuse)
        statusInfos = {
          isSectoriel: collectivitePorteuse.nb_communes > 1 ? collectivitePorteuse.nb_communes < fullDetailsCollecPorteuse.nbCommunes : false,
          hasDelibApprob: rawPlanProcedure.events.some(e => e.libtypeevenement === "Délibération d'approbation" && e.codestatutevenement === 'V'),
          hasAbandon: rawPlanProcedure.events.some(e => ['Abandon', 'Abandon de la procédure'].includes(e.libtypeevenement)),
          hasAnnulation: rawPlanProcedure.events.some(e => ['Caducité', 'Annulation de la procédure', 'Procédure caduque', 'Annulation TA'].includes(e.libtypeevenement))
        }
        if (statusInfos.hasAbandon) {
          statusProcedure = 'abandon'
        } else if (statusInfos.hasAnnulation) {
          statusProcedure = 'annule'
        } else if (rawPlanProcedure.datelancement) {
          statusProcedure = 'en cours'
        }

        return { ...rawPlanProcedure, status: statusProcedure, statusInfos, nbCommunesPerimetre: collectivitePorteuse.nb_communes, collectivitePorteuse: _.pick(collectivitePorteuse, ['code_collectivite_porteuse', 'type_collectivite_porteuse']) }
      })
      // Gestion des rollback du a une annuldation de la délibération (le DU précédent en date devient opposable) et précédent
      // La dernière procédure ayant une délibération est l'opposable
      function setSpecificsStatus (arrProcedures) {
        const opposableProc = arrProcedures.findLast(e => e.statusInfos.hasDelibApprob && !e.statusInfos.hasAbandon && !e.statusInfos.hasAnnulation)
        if (opposableProc) { opposableProc.status = 'opposable' }
        arrProcedures.filter(e => e.statusInfos.hasDelibApprob && opposableProc.noserieprocedure !== e.noserieprocedure).forEach((e) => { e.status = 'precedent' })
      }

      // Définition des procédures secondaires
      const typePrincipalProcedures = ['Elaboration', 'Révision', 'Abrogation', 'Engagement', 'Réengagement']
      const [procsPrincipales, procsSecondaires] = _.partition(planProcedures, procedure => typePrincipalProcedures.includes(procedure.libtypeprocedure))
      let groupedProcsSecondaires = _.groupBy(procsSecondaires, e => e.noserieprocedureratt?.toString())

      // Define specific status for principales / secondaires
      console.log('procsPrincipales ?? : ', procsPrincipales)
      setSpecificsStatus(procsPrincipales)
      console.log('groupedProcsSecondaires ?? : ', groupedProcsSecondaires)
      _.each(groupedProcsSecondaires, e => setSpecificsStatus(e))
      groupedProcsSecondaires = _.groupBy(procsSecondaires, e => e.noserieprocedureratt?.toString())

      console.log('TEST planProcedures: ', planProcedures)

      // Assign procedures secondaire to principales
      const fullProcs = _.map(procsPrincipales, (procedurePrincipale) => {
        procedurePrincipale.procSecs = groupedProcsSecondaires[procedurePrincipale.noserieprocedure]
        return procedurePrincipale
      })

      return fullProcs
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
