(async () => {
  const { PG_TEST_CONFIG, PG_DEV_CONFIG, PG_PROD_CONFIG } = require('./pg_secret_config.json')
  const { createClient } = require('@supabase/supabase-js')

  const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', PG_PROD_CONFIG.admin_key)
  const axios = require('axios')
  const epcis = require('../server-middleware/Data/EnrichedIntercommunalites.json')
  const communes = require('../server-middleware/Data/EnrichedCommunes.json')

  console.log('Starting importing Sudocuh to Docurba...')

  async function createFullProcedure (procedure, { isPrincipale, docurbaProcedurePrincipaleId, docurbaProjectPrincipaleId, collectivite }) {
    const docType = procedure.perimetre > 1 && procedure.doc_type === 'PLU' ? `${procedure.doc_type}i` : procedure.doc_type

    let docurbaProjectId = docurbaProjectPrincipaleId
    if (isPrincipale) {
      const formattedProject = {
        name: `${docType} de ${procedure.perimetre > 1 ? procedure.collectivite_porteuse.code_collectivite_porteuse : procedure.perimetre[0].name}`,
        doc_type: procedure.doc_type,
        current_perimetre: procedure.perimetre,
        initial_perimetre: procedure.perimetre,
        collectivite_porteuse_id: procedure.collectivite_porteuse.code_collectivite_porteuse,
        from_sudocuh: procedure.id,
        region: collectivite.intercommunalite.regionCode
      }
      // console.log('procedure: ', procedure)
      // console.log('formattedProject: ', formattedProject)
      const { data: insertedProject, error: errorInsertedProject } = await supabase.from('projects').upsert(formattedProject, { onConflict: 'from_sudocuh', ignoreDuplicates: true }).select()
      if (errorInsertedProject) { throw errorInsertedProject }
      console.log('insertedProject: ', insertedProject)
      docurbaProjectId = insertedProject?.[0]?.id
      if (insertedProject.length === 0) {
        docurbaProjectId = (await supabase.from('projects').select().eq('from_sudocuh', procedure.id)).data[0].id
      }
    }
    const formattedProcedure = {
      project_id: docurbaProjectId,
      type: procedure.type,
      commentaire: procedure.description,
      current_perimetre: procedure.perimetre,
      initial_perimetre: procedure.perimetre,
      collectivite_porteuse_id: procedure.collectivite_porteuse.code_collectivite_porteuse,
      from_sudocuh: procedure.id,
      is_principale: isPrincipale,
      status: procedure.status,
      secondary_procedure_of: docurbaProcedurePrincipaleId,
      sudocu_secondary_procedure_of: !isPrincipale && procedure.procedure_id ? procedure.procedure_id : null,
      doc_type: docType,
      is_sectoriel: !!procedure.status_infos?.isSectoriel,
      is_scot: null,
      is_pluih: null,
      is_pdu: null,
      mandatory_pdu: null,
      moe: null, // TODO: Est un object, soit detail sous traitant + cout, sois Interne
      volet_qualitatif: null // TODO: JSON
    }
    console.log('formattedProcedure: ', formattedProcedure)

    const { data: insertedProcedure, error: errorInsertedProcedure } = await supabase.from('procedures').upsert(formattedProcedure, { onConflict: 'from_sudocuh', ignoreDuplicates: true }).select()
    if (errorInsertedProcedure) { throw errorInsertedProcedure }
    console.log('insertedProcedure: ', insertedProcedure)
    let docurbaProcedureId = insertedProcedure?.[0]?.id
    if (insertedProcedure.length === 0) {
      docurbaProcedureId = (await supabase.from('procedures').select().eq('from_sudocuh', procedure.id)).data[0].id
    }
    await insertEvents(procedure.events, { docurbaProcedureId, docurbaProjectId })
    return { docurbaProcedureId, docurbaProjectId }
  }

  async function processProcedures (collectiviteCode) {
    const { collectivite, procedures, schemas } = (await axios({ url: `http://localhost:3000/api/urba/collectivites/${collectiviteCode}`, method: 'get' })).data
    for (const procedure of procedures) {
      const { docurbaProcedureId: docurbaProcedurePrincipaleId, docurbaProjectId: docurbaProjectPrincipaleId } = await createFullProcedure(procedure, { isPrincipale: true, collectivite })
      // console.log(' docurbaProcedureId, docurbaProjectId : ', docurbaProcedurePrincipaleId, docurbaProjectPrincipaleId)
      if (procedure.procSecs && procedure.procSecs.length > 0) {
        for (const procedureSecondaire of procedure.procSecs) {
          await createFullProcedure(procedureSecondaire, { isPrincipale: false, docurbaProcedurePrincipaleId, docurbaProjectPrincipaleId, collectivite })
        }
      }
    }
  }

  async function insertEvents (events, { docurbaProcedureId, docurbaProjectId }) {
    const formattedEvents = events.map((event) => {
      const formattedEvent = {
        project_id: docurbaProjectId,
        procedure_id: docurbaProcedureId,
        type: event.libtypeevenement,
        is_valid: event.codestatutevenement === 'V',
        date_iso: event.dateevenement,
        description: '',
        actors: null, // TODO: Voir si on trouve les noms dans Sudocu
        attachements: null, // TODO: Ajouter proprement le lien attachments
        visibility: 'private',
        from_sudocuh: event.noserieevenement
      }
      return formattedEvent
    })
    const { data: insertedEvents, error: errorInsertedEvents } = await supabase.from('doc_frise_events').upsert(formattedEvents, { onConflict: 'from_sudocuh', ignoreDuplicates: true })
    if (errorInsertedEvents) { throw errorInsertedEvents }
    console.log('insertedEvents: ', insertedEvents)
  }

  try {
    const collectivites = [...communes, ...epcis]
    // const collectivites = communes
    // const collectivites = epcis
    const len = collectivites.length
    // 1221 stopped schema
    const startAt = 0
    const BATCH_SIZE = 60
    const RATE = 200

    for (const [i, collec] of collectivites.entries()) {
      console.log('Processing ', i, ' of ', len, ' - code: ', collec.code)
      await processProcedures(collec.code)
      await new Promise((resolve, reject) => setTimeout(resolve, RATE))
      console.log('Inserted')
    }
  } catch (error) {
    console.log('error: ', error)
  }
})()