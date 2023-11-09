
(async () => {
  const { PG_TEST_CONFIG, PG_DEV_CONFIG, PG_PROD_CONFIG } = require('./pg_secret_config.json')
  const { createClient } = require('@supabase/supabase-js')

  const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', PG_PROD_CONFIG.admin_key)
  const axios = require('axios')
  const epcis = require('../server-middleware/Data/EnrichedIntercommunalites.json')
  const communes = require('../server-middleware/Data/EnrichedCommunes.json')

  console.log('Starting importing Sudocuh to Docurba...')

  async function createFullProcedure (procedure, { isPrincipale, docurbaProcedurePrincipaleId, docurbaProjectPrincipaleId, collectivite, schemaOnly }) {
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
        region: collectivite?.intercommunalite?.regionCode,
        is_sudocuh_scot: schemaOnly
      }
      // console.log('procedure: ', procedure)
      // console.log('formattedProject: ', formattedProject)
      const { data: insertedProject, error: errorInsertedProject } = await supabase.from('projects').upsert(formattedProject, { onConflict: 'from_sudocuh', ignoreDuplicates: false }).select()
      if (errorInsertedProject) { throw errorInsertedProject }
      // console.log('insertedProject: ', insertedProject)
      docurbaProjectId = insertedProject?.[0]?.id
      if (insertedProject.length === 0) {
        docurbaProjectId = (await supabase.from('projects').select().eq('from_sudocuh', procedure.id)).data[0].id
      }
    }

    const formattedProcedure = {
      project_id: docurbaProjectId,
      type: procedure.type,
      scot_name: procedure.name,
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
      is_scot: procedure.is_scot || schemaOnly,
      is_pluih: procedure?.is_pluih,
      is_pdu: procedure?.is_pdu,
      mandatory_pdu: procedure?.mandatory_pdu,
      moe: procedure?.moe,
      volet_qualitatif: procedure?.volet_qualitatif,
      is_sudocuh_scot: schemaOnly,
      test: true
    }
    // console.log('formattedProcedure: ', formattedProcedure)
    // console.log('procedure?.moe: ', procedure?.moe)
    const { data: insertedProcedure, error: errorInsertedProcedure } = await supabase.from('procedures').upsert(formattedProcedure, { onConflict: 'from_sudocuh', ignoreDuplicates: false }).select()
    if (errorInsertedProcedure) { throw errorInsertedProcedure }
    // console.log('insertedProcedure: ', insertedProcedure)
    let docurbaProcedureId = insertedProcedure?.[0]?.id
    if (insertedProcedure.length === 0) {
      docurbaProcedureId = (await supabase.from('procedures').select().eq('from_sudocuh', procedure.id)).data[0].id
    }
    await insertEvents(procedure.events, { docurbaProcedureId, docurbaProjectId, schemaOnly })
    return { docurbaProcedureId, docurbaProjectId }
  }

  async function processProcedures (collectiviteCode, { schemaOnly }) {
    const { collectivite, procedures, schemas } = (await axios({ url: `http://localhost:3000/api/urba/collectivites/${collectiviteCode}`, method: 'get' })).data
    if (!schemaOnly) {
      for (const procedure of procedures) {
        // console.log('procedure: ', procedure)
        const { docurbaProcedureId: docurbaProcedurePrincipaleId, docurbaProjectId: docurbaProjectPrincipaleId } = await createFullProcedure(procedure, { isPrincipale: true, collectivite })
        // console.log('procedure: ', procedure.id, ' ', procedure.doc_type, '  ', procedure.status)
        // console.log(' docurbaProcedureId, docurbaProjectId : ', docurbaProcedurePrincipaleId, docurbaProjectPrincipaleId)
        if (procedure.procSecs && procedure.procSecs.length > 0) {
          for (const procedureSecondaire of procedure.procSecs) {
            await createFullProcedure(procedureSecondaire, { isPrincipale: false, docurbaProcedurePrincipaleId, docurbaProjectPrincipaleId, collectivite })
          }
        }
      }
    } else {
      for (const schema of schemas) {
        const { docurbaProcedureId: docurbaProcedurePrincipaleId, docurbaProjectId: docurbaProjectPrincipaleId } = await createFullProcedure(schema, { isPrincipale: true, collectivite, schemaOnly })
        // console.log(' docurbaProcedureId, docurbaProjectId : ', docurbaProcedurePrincipaleId, docurbaProjectPrincipaleId)
        if (schema.procSecs && schema.procSecs.length > 0) {
          for (const procedureSecondaire of schema.procSecs) {
            await createFullProcedure(procedureSecondaire, { isPrincipale: false, docurbaProcedurePrincipaleId, docurbaProjectPrincipaleId, collectivite, schemaOnly })
          }
        }
      }
    }
  }

  async function insertEvents (events, { docurbaProcedureId, docurbaProjectId, schemaOnly }) {
    const formattedEvents = events?.map((event) => {
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
        from_sudocuh: event.noserieevenement,
        is_sudocuh_scot: schemaOnly
      }
      return formattedEvent
    })
    if (formattedEvents) {
      const { data: insertedEvents, error: errorInsertedEvents } = await supabase.from('doc_frise_events').upsert(formattedEvents, { onConflict: 'from_sudocuh', ignoreDuplicates: false })
      if (errorInsertedEvents) { throw errorInsertedEvents }
    }

    // console.log('insertedEvents: ', insertedEvents)
  }

  try {
    const collectivites = [...communes, ...epcis]
    // const collectivites = communes
    // const collectivites = epcis
    const len = collectivites.length
    // 1221 stopped schema
    const startAt = 2866
    const BATCH_SIZE = 15
    const RATE = 50

    let tempProms = []

    // COmmiune / Procedure qui ne doivent pas etre a en cours
    // 01303 / 61137
    // 56054 / 60401
    // 83004 / 1831
    // 83044 / 14904

    // const testOne = collectivites.find(e => e.code === '83044')
    // console.log('HERE TESt: ', testOne)
    // await processProcedures(testOne.code, { schemaOnly: false })

    for (const [i, collec] of collectivites.entries()) {
      if (i >= startAt) {
        console.log('Processing ', i, ' of ', len, ' - code: ', collec.code)

        const prom = processProcedures(collec.code, { schemaOnly: true })
        await new Promise((resolve, reject) => setTimeout(resolve, RATE))
        tempProms.push(prom)
        if (i % BATCH_SIZE === 0 || len - i < BATCH_SIZE) {
          const batch = await Promise.all(tempProms)
          console.log('Insert ', batch.length, ' in Supabase')
          tempProms = []
        }
      }
    }
  } catch (error) {
    console.log('error: ', error)
  }
})()
