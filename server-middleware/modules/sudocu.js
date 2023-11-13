// TODO: Import supabase
import _ from 'lodash'
import geo from './geo.js'
const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

module.exports = {
  parseAttachment (path) {
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
  },

  partitionProceduresPrincipSecs (collectiviteId, procedures) {
    // Définition des procédures secondaires
    const typePrincipalProcedures = ['Elaboration', 'Révision', 'Abrogation', 'Engagement', 'Réengagement']
    const [procsPrincipales, procsSecondaires] = _.partition(procedures, procedure => typePrincipalProcedures.includes(procedure.type))
    let groupedProcsSecondaires = _.groupBy(procsSecondaires, e => e.procedure_id?.toString())

    // Define specific status for principales / secondaires
    this.setSpecificsStatus(collectiviteId, procsPrincipales)
    // TODO: L'etat des procédure secondaires ne ce defini pas pareil que les principales
    // _.each(groupedProcsSecondaires, procedureSecondaire => this.setSpecificsStatus(collectiviteId, procedureSecondaire))
    groupedProcsSecondaires = _.groupBy(procsSecondaires, e => e.procedure_id?.toString())

    // Assign procedures secondaire to principales
    return _.map(procsPrincipales, (procedurePrincipale) => {
      procedurePrincipale.procSecs = groupedProcsSecondaires[procedurePrincipale.id]
      return procedurePrincipale
    })
  },
  enrich (procedures, proceduresPerimetres, collectivitesPorteuses, { siSchema = false } = {}) {
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

      // siSchema -> partiellement ok
      const isValid = (e, isSchema) => isSchema ? e.codestatutevenement === 'V' : (e.codestatutevenement === 'V' || e.codestatutevenement === 'AT')
      statusInfos = {
        isSectoriel,
        // ou Arrêté d'abrogation OU Arrêté du Maire ou du Préfet ou de l'EPCI OU Approbation du préfet
        hasDelibApprob: procedure.events?.some(e => ["Délibération d'approbation", "Arrêté d'abrogation", "Arrêté du Maire ou du Préfet ou de l'EPCI", 'Approbation du préfet'].includes(e.libtypeevenement) && isValid(e, siSchema)),
        hasAbandon: procedure.events?.some(e => ['Abandon', 'Abandon de la procédure'].includes(e.libtypeevenement)),
        hasAnnulation: procedure.events?.some(e => ['Caducité', 'Annulation de la procédure', 'Procédure caduque', 'Annulation TA'].includes(e.libtypeevenement) && e.codestatutevenement === 'V')
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
  },
  setCommunalsProceduresStatus (arrProcedures) {
    const opposableProc = arrProcedures.find(e => e.status_infos.hasDelibApprob && !e.status_infos.hasAbandon && !e.status_infos.hasAnnulation)
    // console.log('arrProcedures: ', arrProcedures)
    if (opposableProc) {
      opposableProc.status = 'opposable'
      // TODO: ca fait un bug sur Montgaillard
      // || opposableProc.perimetre.length === 1
      arrProcedures.filter(e => (e.status_infos.hasDelibApprob) && !e.status_infos.hasAbandon && !e.status_infos.hasAnnulation && opposableProc.id !== e.id).forEach((e) => { e.status = 'precedent' })
    }
    // console.log('opposableProc:', opposableProc)
  },
  // Gestion des rollback du a une annuldation de la délibération (le DU précédent en date devient opposable) et précédent
  // La dernière procédure ayant une délibération est l'opposable
  setSpecificsStatus (collectiviteId, arrProcedures) {
    if (collectiviteId.length > 5) {
      const opposableProc = arrProcedures.find(e => e.status_infos.hasDelibApprob && !e.status_infos.hasAbandon && !e.status_infos.hasAnnulation && e.perimetre.length > 1)
      if (opposableProc) { opposableProc.status = 'opposable' }

      // Vérification des status des PLUi sectoriels opposable ou precedent
      if (opposableProc && opposableProc.status_infos.isSectoriel) {
        let globalPerimOpp = [arrProcedures[0].perimetre.map(e => e.inseeCode)]
        arrProcedures.forEach((procedure, i) => {
          // On cherche si le perimetre de la procédure PLUi suivante a des commune en commun
          if (i > 0 && procedure.status_infos.isSectoriel && procedure.status_infos.hasDelibApprob && !procedure.status_infos.hasAbandon && !procedure.status_infos.hasAnnulation && procedure.perimetre.length > 1) {
            const procPerimetreCodes = procedure.perimetre.map(e => e.inseeCode)
            const intersec = procPerimetreCodes.filter(code => globalPerimOpp.includes(code))
            if (intersec.length > 0) {
              procedure.status = 'precedent'
            } else {
              procedure.status = 'opposable'
              globalPerimOpp = [...globalPerimOpp, ...procPerimetreCodes]
            }
          }
        })
      } else {
        arrProcedures.filter(e => e.perimetre.length > 1 && e.status_infos.hasDelibApprob && !e.status_infos.hasAbandon && !e.status_infos.hasAnnulation && opposableProc.id !== e.id).forEach((e) => { e.status = 'precedent' })
      }
      // Dans le cas d'un EPCI sans PLUi opposable, on recupere toutes les procédure avec perimetre = 1 (DU Communaux), on les groupe par code INSEE (toutes les procedures pour chaque commune)
      // On applique pour chaque indépendament le test d'opposabilité, puis on reconcatene tout
      const PluisOpp = arrProcedures.filter(e => e.status === 'opposable')
      const noPluiOpp = !arrProcedures.map(e => e.status).includes('opposable')
      const proceduresCommunales = arrProcedures.filter(e => e.perimetre.length === 1)

      if (noPluiOpp) {
        const groupedProceduresCommunals = _.groupBy(proceduresCommunales, e => e.perimetre[0].inseeCode)
        _.map(groupedProceduresCommunals, (proceduresCommune) => {
          this.setCommunalsProceduresStatus(proceduresCommune)
        })
      } else {
        // Si il y a un ou des PLUi opposable, on considère tous les DU des communes qui sont sous le perimètre de ce / ces PLUi(s) comme précédent
        const PluisOppCodePerimetre = PluisOpp.reduce((acc, curr) => [...acc, ...curr.perimetre.map(e => e.inseeCode)], [])
        proceduresCommunales.forEach((procedureCommunale) => {
          // Si la procédure de la commune est dans le pérmietre des PLUi
          const isSousPlui = PluisOppCodePerimetre.includes(procedureCommunale.perimetre[0].inseeCode)
          if (isSousPlui) {
            procedureCommunale.status = 'precedent'
          } else {
            // OU si les perimetres des PLUi opposables ne couvre pas la commune, on recupère les procédures de la commune et on applique le setStatus
            const proceduresHorsPerimetre = arrProcedures.filter(e => e.perimetre[0].inseeCode === procedureCommunale.perimetre[0].inseeCode && e.perimetre.length === 1)
            this.setCommunalsProceduresStatus(proceduresHorsPerimetre)
          }
        })
      }
    } else {
      this.setCommunalsProceduresStatus(arrProcedures)
    }
  },
  async  getProceduresEvents (arrProceduresId) {
    try {
      const rawPlanEvents = await supabase.from('sudocu_procedure_events').select('*').in('noserieprocedure', arrProceduresId).order('dateevenement', { ascending: true })
      const rawSchemaEvents = await supabase.from('sudocu_schemas_events').select('*').in('noserieprocedure', arrProceduresId).order('dateevenement', { ascending: true })
      const [{ data: planEvents, error: errPlanEvents }, { data: schemaEvents, error: errSchemaEvents }] = await Promise.all([rawPlanEvents, rawSchemaEvents])
      if (errPlanEvents) { throw errPlanEvents }
      if (errSchemaEvents) { throw errSchemaEvents }

      const formattedEvs = planEvents.map(e => ({ ...e, attachements: this.parseAttachment(e.nomdocument) }))
      const allEvts = formattedEvs.concat(schemaEvents)
      return _.groupBy(allEvts, e => e.noserieprocedure)
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('ERROR getProcedureEvents:', JSON.stringify(error))
    }
  },
  async  getProceduresCollectivite (collectiviteId) {
    // TODO: Refaire l'import des events avec le code event plutot que uniquement le label

    // On recupère les périmètres des procédures de la commune. Si c'est une EPCI on filtre sur la collectivite porteuse
    try {
      const proceduresCollecQuery = supabase.from('sudocu_procedures_perimetres').select('*')
      collectiviteId = collectiviteId.toString().padStart(5, '0')

      let proceduresCollec = null
      if (collectiviteId.length > 5) {
        proceduresCollec = await proceduresCollecQuery.eq('code_collectivite_porteuse', collectiviteId)
      } else {
        proceduresCollec = await proceduresCollecQuery.contains('communes_insee', [collectiviteId])
      }
      if (proceduresCollec.error) { throw proceduresCollec }
      const proceduresCollecIds = proceduresCollec.data.map(e => e.procedure_id)

      // On fetch les procédures faisant parti du périmètre de la commune
      const rawPlanProcedures = await supabase.from('distinct_procedures_events').select('*').in('noserieprocedure', proceduresCollecIds).order('last_event_date', { ascending: false }).order('dateapprobation', { ascending: false }) // .order([{ column: 'last_event_date', order: 'desc' }, { column: 'dateapprobation', order: 'desc' }])
      console.log('rawPlanProcedures: ', rawPlanProcedures.data[0])
      const rawSchemaProcedures = await supabase.from('distinct_procedures_schema_events').select('*').in('noserieprocedure', proceduresCollecIds).order('last_event_date', { ascending: false })
      if (rawPlanProcedures.error) { throw rawPlanProcedures }
      if (rawSchemaProcedures.error) { throw rawSchemaProcedures }
      // On fetch tous les events liées aux procédures

      const allProceduresEvents = await this.getProceduresEvents(proceduresCollecIds)

      // Fetch des collectivités porteuses des différentes procédures
      const collecsPorteusesIds = [...new Set(proceduresCollec.data.map(e => e.code_collectivite_porteuse))]
      const collectivitesPorteuses = geo.getCollectivites(collecsPorteusesIds)

      // Raccordement des events à leur procédure
      const planProceduresEvents = rawPlanProcedures.data.map(procedure => ({ ...procedure, events: allProceduresEvents[procedure.noserieprocedure] }))
      const schemaProceduresEvents = rawSchemaProcedures.data.map(procedure => ({ ...procedure, events: allProceduresEvents[procedure.noserieprocedure] }))

      const planProcedures = this.enrich(planProceduresEvents, proceduresCollec, collectivitesPorteuses)
      const schemaProcedures = this.enrich(schemaProceduresEvents, proceduresCollec, collectivitesPorteuses, { isSchema: true })

      // Formattage des procédures
      const formattedSchemaProcedures = schemaProcedures.map((e) => {
        return {
          ...e,
          id: e.noserieprocedure,
          name: e.nomschema,
          type: e.libtypeprocedure,
          procedure_id: e.noserieprocedureratt,
          status_infos: e.statusInfos,
          doc_type: e.doc_type,
          description: e.commentaire,
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
          status: e.status
        }
      })
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
          status_infos: e.statusInfos,
          volet_qualitatif: e.volet_qualitatif,
          is_scot: e.is_scot,
          is_pluih: e.is_pluih,
          is_pdu: e.is_pdu,
          mandatory_pdu: e.mandatory_pdu,
          moe: e.moe
        }
      })

      const fullProcs = this.partitionProceduresPrincipSecs(collectiviteId, formattedProcedures)
      const fullSchemas = this.partitionProceduresPrincipSecs(collectiviteId, formattedSchemaProcedures)

      const collectivite = geo.getCollectivite(collectiviteId)
      // procedures: fullProcs
      // console.log('collectivite: ', collectivite, ' : ', fullProcs)
      // console.log('collectivite: ', collectivite)
      return { collectivite, procedures: fullProcs, schemas: fullSchemas }
    } catch (error) {
      console.log('ERROR: ', error)
    }
  }
}
