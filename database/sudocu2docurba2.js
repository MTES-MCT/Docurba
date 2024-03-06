(async () => {
  const { PG_TEST_CONFIG, PG_DEV_CONFIG, PG_PROD_CONFIG } = require('./pg_secret_config.json')
  const { createClient } = require('@supabase/supabase-js')
  const _ = require('lodash')
  const fs = require('fs')

  const supabaseSource = createClient(PG_DEV_CONFIG.url, PG_DEV_CONFIG.admin_key, {
    auth: { persistSession: false }
  })

  const supabase = createClient(PG_PROD_CONFIG.url, PG_PROD_CONFIG.admin_key, {
    auth: { persistSession: false }
  })

  // const axios = require('axios')
  const epcis = require('../server-middleware/Data/referentiels/groupements.json')
  const communes = require('../server-middleware/Data/referentiels/communes.json')

  const PROCEDURES_TYPES = require('./miscs/procedureTypes.json')
  const DOCUMENTS_TYPES = require('./miscs/documentTypes.json')

  /// ///////////////////////////////////
  /// /////////// HELPERS  //////////////
  /// ///////////////////////////////////

  function getDocType (docTypeId) {
    return DOCUMENTS_TYPES.find(e => e.noserietypedocument === docTypeId)
  }

  function getProcedureType (procedureTypeId) {
    return PROCEDURES_TYPES.find(e => e.noserietypeprocedure === procedureTypeId)
  }

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

  let pageSize = 10000
  let currentPage = 1
  let hasMore = true
  /// ////////////////////////////////////////////////////////
  /// /////////// PROJECTS & PROCS. PRINCIPALES //////////////
  /// ////////////////////////////////////////////////////////

  console.log('Starting processing procedures principales.')
  while (hasMore) {
    const { data: dataProcedures, error: errorProcedures } = await supabaseSource.from('sudocu_procedure_plan')
      .select('*')
      .in('noserietypeprocedure', PROCEDURES_TYPES.filter(e => e.siprocedureprincipale).map(e => e.noserietypeprocedure))
      .order('noserieprocedure', { ascending: true })
      .range((currentPage - 1) * pageSize, currentPage * pageSize - 1)
      .limit(pageSize)
    if (errorProcedures) { console.log(errorProcedures) }
    if (dataProcedures && dataProcedures.length > 0) {
      console.log('Processing page: ', currentPage)

      const formattedProcedures = dataProcedures?.map((procedure) => {
        const currDocType = getDocType(procedure.noserietypedocument)
        const currProcType = getProcedureType(procedure.noserietypeprocedure)
        if (!currDocType) {
          console.log(procedure.noserietypedocument)
        }
        if (!currProcType) {
          console.log(procedure.noserietypeprocedure)
        }
        return {
          project_id: null,
          type: currProcType.libtypeprocedure,
          type_code: currProcType.codetypeprocedure,
          name: null,
          commentaire: procedure.commentaireproc,
          departements: null, // TODO: Ajouter par rapport au referentiel
          current_perimetre: procedure.perimetre,
          initial_perimetre: procedure.perimetre,
          collectivite_porteuse_id: procedure.codecollectivite,
          from_sudocuh: procedure.noserieprocedure,
          is_principale: true,
          status: null, // DONE BY TRIGGER
          doc_type_code: currDocType.codetypedocument,
          doc_type: currDocType.libtypedocument,
          is_sectoriel: procedure.sisectoriel,
          is_scot: !!(procedure.sipluiscot), // || schemaOnly// TODO: Mettre a true si le doctype est scot
          is_pluih: procedure.siplhpluih,
          is_pdu: procedure.sipdu,
          mandatory_pdu: procedure.siobligationpdu,
          moe: procedure?.moe,
          volet_qualitatif: procedure?.volet_qualitatif,
          numero: procedure.noprocedure
        }
      })
      console.log('To Upsert ', formattedProcedures.length, ' procedures principales.')
      // Fait le bulk upsert de procédures et récupérer les nouvelles
      const { data: insertedProcedures, error: errorInsertedProcedure } = await supabase.from('procedures_duplicate')
        .upsert(formattedProcedures, { onConflict: 'from_sudocuh', ignoreDuplicates: true })
        .select()
      if (errorInsertedProcedure) { console.log(errorInsertedProcedure) }
      console.log('Upserted ', insertedProcedures?.length, ' procedures principales.')
      // On créer des projects pour toutes les nouvelles procedures principales

      const formattedProjects = dataProcedures.map((procedure) => {
        const currDocType = getDocType(procedure.noserietypedocument)
        return {
          name: null, // `${docType} de ${procedure.perimetre > 1 ? procedure.collectivite_porteuse.code_collectivite_porteuse : procedure.perimetre[0].name}`,
          doc_type_code: currDocType.codetypedocument,
          doc_type: currDocType.libtypedocument,
          current_perimetre: procedure.perimetre,
          initial_perimetre: procedure.perimetre,
          collectivite_porteuse_id: procedure.codecollectivite,
          from_sudocuh_procedure_id: procedure.noserieprocedure,
          region: null
        }
      })
      const { data: insertedProjects, error: errorInsertedProjects } = await supabase.from('projects_duplicate')
        .upsert(formattedProjects, { onConflict: 'from_sudocuh_procedure_id', ignoreDuplicates: true })
        .select()

      if (errorInsertedProjects) { console.log(errorInsertedProjects) }
      console.log('Upserted ', insertedProjects?.length, ' projects.')
      // Update les nouvelles procédure pour leur assigner leur id_project
      // Ajouter les projects uniquement sur ceux insert dans un second temps
      if (insertedProjects) {
        // , from_sudocuh: e.from_sudocuh_procedure_id
        const toUpsertProceduresProjectsIds = insertedProjects.map(e => ({ project_id: e.id, from_sudocuh: e.from_sudocuh_procedure_id }))
        const { data: dataProceduresNewProject, error: errorProceduresNewProject } = await supabase.from('procedures_duplicate')
          .upsert(toUpsertProceduresProjectsIds, { onConflict: 'from_sudocuh', ignoreDuplicates: false }).select()
        if (errorProceduresNewProject) { console.log(errorProceduresNewProject) }
        console.log('Upserted ', dataProceduresNewProject?.length, ' procedures with a project_id.')
      }
      currentPage++
    } else { hasMore = false }
  }

  // TODO: Get in memory newly added procédures

  console.log('End processing for procedures principales.')

  /// ////////////////////////////////////////
  /// /////////// PROCS SECONDAIRES //////////
  /// ////////////////////////////////////////

  currentPage = 1
  hasMore = true

  console.log('Starting processing procedures secondaires.')
  while (hasMore) {
    const { data: dataProceduresSecs, error: errorProceduresSecs } = await supabaseSource.from('sudocu_procedure_plan')
      .select('*')
      .in('noserietypeprocedure', PROCEDURES_TYPES.filter(e => !e.siprocedureprincipale).map(e => e.noserietypeprocedure))
      .order('noserieprocedure', { ascending: true })
      .range((currentPage - 1) * pageSize, currentPage * pageSize - 1)
      .limit(pageSize)
    if (errorProceduresSecs) { console.log(errorProceduresSecs) }
    if (dataProceduresSecs && dataProceduresSecs.length > 0) {
      console.log('[PROC. SEC.] Processing page: ', currentPage)
      const formattedProcedures = dataProceduresSecs?.map((procedure) => {
        const currDocType = getDocType(procedure.noserietypedocument)
        const currProcType = getProcedureType(procedure.noserietypeprocedure)
        if (!currDocType) {
          console.log(procedure.noserietypedocument)
        }
        if (!currProcType) {
          console.log(procedure.noserietypeprocedure)
        }
        return {
          project_id: null,
          type: currProcType.libtypeprocedure,
          type_code: currProcType.codetypeprocedure,
          name: null,
          commentaire: procedure.commentaireproc,
          departements: null, // TODO: Ajouter par rapport au referentiel
          current_perimetre: procedure.perimetre,
          initial_perimetre: procedure.perimetre,
          collectivite_porteuse_id: procedure.codecollectivite,
          from_sudocuh: procedure.noserieprocedure,
          is_principale: false,
          status: null,
          secondary_procedure_of: null,
          sudocu_secondary_procedure_of: null,
          doc_type_code: currDocType.codetypedocument,
          doc_type: currDocType.libtypedocument,
          is_sectoriel: procedure.sisectoriel,
          is_scot: !!(procedure.sipluiscot), // || schemaOnly// TODO: Mettre a true si le doctype est scot
          is_pluih: procedure.siplhpluih,
          is_pdu: procedure.sipdu,
          mandatory_pdu: procedure.siobligationpdu,
          moe: procedure?.moe,
          volet_qualitatif: procedure?.volet_qualitatif,
          numero: procedure.noprocedure
        }
      })
      console.log('To Upsert ', formattedProcedures.length, ' procedures secondaires.')
      // Fait le bulk upsert de procédures secondaires
      const { data: insertedProcedures, error: errorInsertedProcedure } = await supabase.from('procedures_duplicate').upsert(formattedProcedures, { onConflict: 'from_sudocuh', ignoreDuplicates: true }).select()
      if (errorInsertedProcedure) { console.log(errorInsertedProcedure) }
      console.log('Upserted ', insertedProcedures.length, ' procedures secondaires.')
      currentPage++
    } else { hasMore = false }
  }

  console.log('End processing for procedures secondaires.')

  /// //////////////////////////////////////////////////////////////////
  /// /////////// MAPPING ID PROCEDURES SUDOCU / DOCURBA  //////////////
  /// //////////////////////////////////////////////////////////////////
  currentPage = 1
  hasMore = true

  console.log('Starting mapping id procedures sudocu / docurba')
  let proceduresMapping = []
  while (hasMore) {
    const ret = await supabase.from('procedures_duplicate')
      .select('id, project_id, from_sudocuh')
      .order('id', { ascending: true })
      .range((currentPage - 1) * pageSize, currentPage * pageSize - 1)
      .limit(pageSize)
    if (ret.error) { console.log(ret.error) }
    if (ret.data && ret.data.length > 0) {
      proceduresMapping = [...proceduresMapping, ...ret.data]
      currentPage++
    } else { hasMore = false }
  }
  // console.log('proceduresMapping: ', proceduresMapping.slice(0, 30))

  try {
    fs.writeFileSync('./database/miscs/output.json', JSON.stringify(proceduresMapping), { flag: 'w' })
    console.log('Array successfully written to file.')
  } catch (error) {
    console.error('Error writing array to file:', error)
  }

  console.log('End mapping ' + proceduresMapping.length + ' id procedures sudocu / docurba')

  /// ////////////////////////////////////////
  /// /////////// UPSERT EVENTS //////////////
  /// ////////////////////////////////////////

  currentPage = 1
  pageSize = 10000
  hasMore = true

  console.log('Starting processing events.')
  while (hasMore) {
    const { data: dataEvents, error: errorEvents } = await supabaseSource.from('sudocu_procedure_events')
      .select('*')
      .order('noserieevenement', { ascending: true })
      .range((currentPage - 1) * pageSize, currentPage * pageSize - 1)
      .limit(pageSize)
    if (errorEvents) { console.log(errorEvents) }
    if (dataEvents && dataEvents.length > 0) {
      console.log('[EVENTS] Processing page: ', currentPage)
      const formattedEvents = dataEvents?.map((event) => {
        const mapped = proceduresMapping.find(e => e.from_sudocuh === event.noserieprocedure)
        if (!mapped) {
          console.log('event: ', event, ' mapped: ', mapped)
        }

        const formattedEvent = {
          // TODO: Attention, vérifier pour les secondaires qui ne devrait pas avoir de project_id associé
          // TODO: Ajouter l'idprocedure sudocuh
          project_id: mapped.project_id,
          procedure_id: mapped.id,
          from_sudocuh_procedure_id: event.noserieprocedure,
          type: event.libtypeevenement,
          code: event.codetypeevenement,
          is_valid: event.codestatutevenement === 'V' || event.codestatutevenement === 'AP',
          date_iso: event.dateevenement,
          description: event.commentaire,
          attachements: parseAttachment(event.nomdocument),
          visibility: 'private',
          from_sudocuh: event.noserieevenement
        }
        // console.log('code: ', formattedEvent.code)
        return formattedEvent
      })
      console.log('Mapped ', currentPage, formattedEvents?.length)
      // TODO: On bulk upsert les nouveaux events
      const { data: insertedEvents, error: errorInsertedEvents } = await supabase.from('doc_frise_events_duplicate').upsert(formattedEvents, { onConflict: 'from_sudocuh', ignoreDuplicates: false })
      if (errorInsertedEvents) { console.log(errorInsertedEvents) }
      currentPage++
    } else { hasMore = false }
  }
  console.log('End processing events.')
  return true
})()
