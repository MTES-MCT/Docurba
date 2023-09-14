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
        const { data: dgdItems, error: infosDgdError } = await $supabase.from('sudocu_procedures_infosdgd').select('*').eq('procedure_id', procedureId)
        const { data: procedure, error: procedureError } = await $supabase.from('distinct_procedures_events').select('*').eq('noserieprocedure', procedureId)
        if (infosDgdError) { throw infosDgdError }
        if (procedureError) { throw procedureError }
        console.log('DGD proced:', procedure)
        const collectivite = await $urbanisator.getCollectivite(procedure[0].codecollectivite)
        return { procedureId, commentaire: procedure[0].commentairedgd, dgdItems, collectivite }
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
      console.log('proceduresCollec.data: ', proceduresCollec.data)
      const proceduresCollecIds = proceduresCollec.data.map(e => e.procedure_id)

      // On fetch les procédures faisant parti du périmètre de la commune
      const rawPlanProcedures = await $supabase.from('distinct_procedures_events').select('*').in('noserieprocedure', proceduresCollecIds).order('last_event_date', { ascending: false })
      const rawSchemaProcedures = await $supabase.from('distinct_procedures_schema_events').select('*').in('noserieprocedure', proceduresCollecIds).order('last_event_date', { ascending: false })
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
        communesPorteuses = (await axios({ url: '/api/geo/communes', method: 'get', params: { codes: communesPorteusesIds } })).data

        console.log('COMMUNES PORTEUSES: ', communesPorteuses)
      }

      const collectivitesPorteuses = epcisPorteuses.concat(communesPorteuses)
      console.log('collectivitesPorteuses: ', collectivitesPorteuses)
      // Raccordement des events à leur procédure
      const planProceduresEvents = rawPlanProcedures.data.map(procedure => ({ ...procedure, events: allProceduresEvents[procedure.noserieprocedure] }))
      const schemaProceduresEvents = rawSchemaProcedures.data.map(procedure => ({ ...procedure, events: allProceduresEvents[procedure.noserieprocedure] }))

      function enrich (procedures, proceduresPerimetres, collectivitesPorteuses) {
        return procedures.map((procedure, idx) => {
        // Raccordements des périmètres aux procédures
          const collecPerim = proceduresPerimetres.data.find(i => i.procedure_id === procedure.noserieprocedure)
          procedure.perimetre = collecPerim.communes_insee.reduce((acc, curr, idx) => {
            acc.push({ inseeCode: collecPerim.communes_insee[idx], name: collecPerim.name_communes[idx] })
            return acc
          }, [])
          // Enrichissement des collectivités porteuses de chaque procédures
          const collectivitePorteuse = proceduresPerimetres.data.find(e => e.procedure_id === procedure.noserieprocedure)
          let statusProcedure = 'inconnu'
          let statusInfos = {}

          // Vérification de la sectorialité - si le périmètre de la procédure est plus petit que la collectivité porteuse
          const fullDetailsCollecPorteuse = collectivitesPorteuses.find(e => e.code === collectivitePorteuse.code_collectivite_porteuse)

          let isSectoriel = null
          if (fullDetailsCollecPorteuse?.nbCommunes) {
            isSectoriel = collectivitePorteuse.nb_communes > 1 ? collectivitePorteuse.nb_communes < fullDetailsCollecPorteuse.nbCommunes : false
          }
          statusInfos = {
            isSectoriel, // collectivitePorteuse.nb_communes > 1 ? collectivitePorteuse.nb_communes < fullDetailsCollecPorteuse.nbCommunes : false,
            hasDelibApprob: procedure.events?.some(e => e.libtypeevenement === "Délibération d'approbation" && e.codestatutevenement === 'V'),
            hasAbandon: procedure.events?.some(e => ['Abandon', 'Abandon de la procédure'].includes(e.libtypeevenement)),
            hasAnnulation: procedure.events?.some(e => ['Caducité', 'Annulation de la procédure', 'Procédure caduque', 'Annulation TA'].includes(e.libtypeevenement))
          }
          if (statusInfos.hasAbandon) {
            statusProcedure = 'abandon'
          } else if (statusInfos.hasAnnulation) {
            statusProcedure = 'annule'
          } else if (procedure.datelancement) {
            statusProcedure = 'en cours'
          }

          const nameDocType = procedure.perimetre > 1 && procedure.codetypedocument === 'PLU' ? procedure.codetypedocument + 'i' : procedure.codetypedocument
          return { ...procedure, doc_type: nameDocType, status: statusProcedure, statusInfos, nbCommunesPerimetre: collectivitePorteuse.nb_communes, collectivitePorteuse: _.pick(collectivitePorteuse, ['code_collectivite_porteuse', 'type_collectivite_porteuse']) }
        })
      }

      const planProcedures = enrich(planProceduresEvents, proceduresCollec, collectivitesPorteuses)
      const schemaProcedures = enrich(schemaProceduresEvents, proceduresCollec, collectivitesPorteuses)

      // Gestion des rollback du a une annuldation de la délibération (le DU précédent en date devient opposable) et précédent
      // La dernière procédure ayant une délibération est l'opposable
      function setSpecificsStatus (arrProcedures) {
        const opposableProc = arrProcedures.find(e => e.status_infos.hasDelibApprob && !e.status_infos.hasAbandon && !e.status_infos.hasAnnulation)
        if (opposableProc) { opposableProc.status = 'opposable' }
        arrProcedures.filter(e => e.status_infos.hasDelibApprob && !e.status_infos.hasAbandon && !e.status_infos.hasAnnulation && opposableProc.id !== e.id).forEach((e) => { e.status = 'precedent' })
      }

      // Formattage des procédures

      // TODO: Faire un formatage special Schema
      const formattedSchemaProcedures = schemaProcedures.map((e) => {
        return {
          ...e,
          id: e.noserieprocedure,
          name: e.nomschema,
          type: e.libtypeprocedure,
          procedure_id: e.noserieprocedureratt,
          status_infos: e.statusInfos
        }
      })
      console.log('formattedSchemaProcedures SCHEMA: ', formattedSchemaProcedures)

      const formattedProcedures = planProcedures.map((e) => {
        return {
          actors: [],
          attachements: [],
          id: e.noserieprocedure,
          doc_type: e.doc_type,
          description: e.commentaire,
          type: e.libtypeprocedure,
          procedure_id: e.noserieprocedureratt,
          launch_date: e.datelancement,
          approval_date: e.dateapprobation,
          abort_date: e.dateabandon,
          enforceable_date: e.dateexecutoire,
          created_at: e.datelancement,
          last_updated_at: e.last_event_date,
          collectivite_porteuse: e.collectivitePorteuse,
          events: e.events,
          perimetre: e.perimetre,
          procSecs: e.procSecs,
          status: e.status,
          status_infos: e.statusInfos
        }
      })
      console.log('formattedProcedures: ', formattedProcedures)

      function partitionProceduresPrincipSecs (procedures) {
        // Définition des procédures secondaires
        const typePrincipalProcedures = ['Elaboration', 'Révision', 'Abrogation', 'Engagement', 'Réengagement']
        const [procsPrincipales, procsSecondaires] = _.partition(procedures, procedure => typePrincipalProcedures.includes(procedure.type))
        let groupedProcsSecondaires = _.groupBy(procsSecondaires, e => e.procedure_id?.toString())

        // Define specific status for principales / secondaires

        setSpecificsStatus(procsPrincipales)

        _.each(groupedProcsSecondaires, e => setSpecificsStatus(e))
        groupedProcsSecondaires = _.groupBy(procsSecondaires, e => e.procedure_id?.toString())

        // Assign procedures secondaire to principales
        return _.map(procsPrincipales, (procedurePrincipale) => {
          procedurePrincipale.procSecs = groupedProcsSecondaires[procedurePrincipale.id]
          return procedurePrincipale
        })
      }
      const fullProcs = partitionProceduresPrincipSecs(formattedProcedures)
      const fullSchemas = partitionProceduresPrincipSecs(formattedSchemaProcedures)

      const collectivite = (await axios({
        url: `/api/geo/${collectiviteId.length > 5 ? 'intercommunalites' : 'communes'}/${collectiviteId}`,
        method: 'get'
      })).data

      return { collectivite, procedures: fullProcs, schemas: fullSchemas }
    }
  })
}
