
import fs from 'fs'
import { AsyncParser } from '@json2csv/node'
import { createClient } from '@supabase/supabase-js'
import DOCUMENTS_TYPES from '../miscs/documentTypes.mjs'
import PROCEDURES_TYPES from '../miscs/proceduresTypes.mjs'
import communesReferentiel from '../miscs/referentiels/communes.json' assert {type: 'json'}
import { updateProcedureSec } from './linkProceduresSecs.mjs'
import { appendToGithubSummary } from '../common.mjs'

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}_${month}_${day}`;
}

const currentDate = new Date();

var outputDir = `./daily_dump/output/${formatDate(currentDate)}`;

if (!fs.existsSync(outputDir)){
    fs.mkdirSync(outputDir, { recursive: true });
}

async function sudocuhPlanToDocurba (configSource, configTraget) {
  const supabaseSource = createClient(configSource.url, configSource.admin_key, {
    auth: { persistSession: false }
  })

  const supabase = createClient(configTraget.url, configTraget.admin_key, {
    auth: { persistSession: false }
  })

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
  let addedBufferProcedures = []
  let addedBufferProjects = []
  /// ////////////////////////////////////////////////////////
  /// /////////// PROJECTS & PROCS. PRINCIPALES //////////////
  /// ////////////////////////////////////////////////////////

  // TODO: Opti en commencant par add les projects ?

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
          doc_type: currDocType.codetypedocument,
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
      const { data: insertedProcedures, error: errorInsertedProcedure } = await supabase.from('procedures')
        .upsert(formattedProcedures, { onConflict: 'from_sudocuh', ignoreDuplicates: true })
        .select()
      if (errorInsertedProcedure) { console.log(errorInsertedProcedure) }
      console.log('Upserted ', insertedProcedures?.length, ' procedures principales.')
      // On bufferise pour avoir un CSV par la suite
      addedBufferProcedures = [...addedBufferProcedures, ...insertedProcedures]

      // On créer des projects pour toutes les nouvelles procedures principales
      const formattedProjects = dataProcedures.map((procedure) => {
        const currDocType = getDocType(procedure.noserietypedocument)
        return {
          name: null, // `${docType} de ${procedure.perimetre > 1 ? procedure.collectivite_porteuse.code_collectivite_porteuse : procedure.perimetre[0].name}`,
          doc_type_code: currDocType.codetypedocument,
          doc_type: currDocType.codetypedocument,
          current_perimetre: procedure.perimetre,
          initial_perimetre: procedure.perimetre,
          collectivite_porteuse_id: procedure.codecollectivite,
          from_sudocuh_procedure_id: procedure.noserieprocedure,
          region: null
        }
      })
      const { data: insertedProjects, error: errorInsertedProjects } = await supabase.from('projects')
        .upsert(formattedProjects, { onConflict: 'from_sudocuh_procedure_id', ignoreDuplicates: true })
        .select()

      if (errorInsertedProjects) { console.log(errorInsertedProjects) }
      console.log('Upserted ', insertedProjects?.length, ' projects.')
      // On bufferise pour avoir un CSV par la suite
      addedBufferProjects = [...addedBufferProjects, ...insertedProjects]

      // Update les nouvelles procédure pour leur assigner leur id_project
      // Ajouter les projects uniquement sur ceux insert dans un second temps
      if (insertedProjects) {
        // , from_sudocuh: e.from_sudocuh_procedure_id
        const toUpsertProceduresProjectsIds = insertedProjects.map(e => ({ project_id: e.id, from_sudocuh: e.from_sudocuh_procedure_id }))
        const { data: dataProceduresNewProject, error: errorProceduresNewProject } = await supabase.from('procedures')
          .upsert(toUpsertProceduresProjectsIds, { onConflict: 'from_sudocuh', ignoreDuplicates: false }).select()
        if (errorProceduresNewProject) { console.log(errorProceduresNewProject) }
        console.log('Upserted ', dataProceduresNewProject?.length, ' procedures with a project_id.')
      }
      currentPage++
    } else { hasMore = false }
  }

  const parser = new AsyncParser()
  if (addedBufferProjects.length > 0) {
    const csvNewProjects = await parser.parse(addedBufferProjects).promise()
    try {
      fs.writeFileSync(`${outputDir}/last_projects_added.csv`, csvNewProjects, { flag: 'w' })
      console.log('Projects successfully written to file.')
    } catch (error) {
      console.error('Error writing array to file:', error)
    }
  } else {
    console.log('No new projects. File wont be written in output')
  }
  appendToGithubSummary(`- ${addedBufferProjects.length} nouveaux projets`)


  if (addedBufferProcedures.length > 0) {
    const csvNewProcedures = await parser.parse(addedBufferProcedures).promise()
    try {
      fs.writeFileSync(`${outputDir}/last_procedures_principales_added.csv`, csvNewProcedures, { flag: 'w' })
      console.log('Procedures successfully written to file.')
    } catch (error) {
      console.error('Error writing array to file:', error)
    }
  } else {
    console.log('No new procedures. File wont be written in output')
  }
  appendToGithubSummary(`- ${addedBufferProcedures.length} nouvelles procédures principales`)

  // TODO: Get in memory newly added procédures

  console.log('End processing for procedures principales.')

  /// ////////////////////////////////////////
  /// /////////// PROCS SECONDAIRES //////////
  /// ////////////////////////////////////////

  let addedBufferProceduresSec = []
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
          sudocu_secondary_procedure_of: procedure.noserieprocedureatt,
          doc_type_code: currDocType.codetypedocument,
          doc_type: currDocType.codetypedocument,
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
      const { data: insertedProcedures, error: errorInsertedProcedure } = await supabase.from('procedures').upsert(formattedProcedures, { onConflict: 'from_sudocuh', ignoreDuplicates: true }).select()
      if (errorInsertedProcedure) { console.log(errorInsertedProcedure) }
      addedBufferProceduresSec = [...addedBufferProceduresSec, ...insertedProcedures]
      console.log('Upserted ', insertedProcedures.length, ' procedures secondaires.')
      currentPage++
    } else { hasMore = false }
  }

  if (addedBufferProceduresSec.length > 0) {
    const csvNewProcedures = await parser.parse(addedBufferProceduresSec).promise()
    try {
      fs.writeFileSync(`${outputDir}/last_procedures_secondaires_added.csv`, csvNewProcedures, { flag: 'w' })
      console.log('Procedures successfully written to file.')
    } catch (error) {
      console.error('Error writing array to file:', error)
    }
  } else {
    console.log('No new procedures. File wont be written in output')
  }
  appendToGithubSummary(`- ${addedBufferProceduresSec.length} nouvelles procédures secondaires`)
  console.log('End processing for procedures secondaires.')

  /// ////////////////////////////////////
  /// ///////////PERIMETRE  //////////////
  /// ////////////////////////////////////
  let allAddedBufferProcedures = [...addedBufferProcedures, ...addedBufferProceduresSec]

  console.log('Starting processing perimeters.')
  const formattedPerimetre = allAddedBufferProcedures
    .filter(e => e.current_perimetre)
    .map((procedure) => {
      return procedure.current_perimetre.map((commune) => {
        const comDetail = communesReferentiel.find(e => e.code === commune.inseeCode)
        if (!comDetail) {
          console.log('Not found: ', commune)
        }
        // console.log(commune.departementCode, ' -- ', commune)
        return {
          collectivite_code: commune.inseeCode,
          collectivite_type: comDetail?.type ?? 'UNKWN',
          procedure_id: procedure.id,
          departement: comDetail?.departementCode ?? 'UNKWN',
          opposable: false
        }
      })
    })
    .flat()

  // TODO: Voir le cas ou on part de 0, il y a surement de la pagination
  const { data: perimetersInserted, error } = await supabase.from('procedures_perimetres').upsert(formattedPerimetre, { onConflict: 'collectivite_code,procedure_id,collectivite_type', ignoreDuplicates: true }).select()
  if (error) { console.log(error) }
  console.log("Added nb perimeter: ", perimetersInserted?.length )
  if (perimetersInserted?.length > 0) {
    const csvNewPerimeters = await parser.parse(perimetersInserted).promise()
    try {
      fs.writeFileSync(`${outputDir}/last_perimeter_added.csv`, csvNewPerimeters, { flag: 'w' })
      console.log('Perimeters successfully written to file.')
    } catch (error) {
      console.error('Error writing array to file:', error)
    }
  } else {
    console.log('No new perimeters. File wont be written in output')
  }
  appendToGithubSummary(`- ${perimetersInserted?.length} nouveaux périmètres`)
  console.log('End processing for procedures perimetres.')

  /// //////////////////////////////////////////////////////////////////
  /// /////////// MAPPING ID PROCEDURES SUDOCU / DOCURBA  //////////////
  /// //////////////////////////////////////////////////////////////////
  currentPage = 1
  hasMore = true

  console.log('Starting mapping id procedures sudocu / docurba')
  let proceduresMapping = []
  while (hasMore) {
    const ret = await supabase.from('procedures')
      .select('id, project_id, from_sudocuh, sudocu_secondary_procedure_of, secondary_procedure_of, is_principale')
      .order('id', { ascending: true })
      .range((currentPage - 1) * pageSize, currentPage * pageSize - 1)
      .limit(pageSize)
    if (ret.error) { console.log(ret.error) }
    if (ret.data && ret.data.length > 0) {
      proceduresMapping = [...proceduresMapping, ...ret.data]
      currentPage++
    } else { hasMore = false }
  }


  try {
    fs.writeFileSync(`${outputDir}/mapping_procedures_docurba_sudocuh.json`, JSON.stringify(proceduresMapping), { flag: 'w' })
    console.log('Array successfully written to file.')
  } catch (error) {
    console.error('Error writing array to file:', error)
  }

  console.log('End mapping ' + proceduresMapping.length + ' id procedures sudocu / docurba')

  /// ///////////////////////////////////////////////////////////////////////////
  /// /////////// MAPPING ID PROCEDURES PRINCIPALES / SECONDAIRES  //////////////
  /// ///////////////////////////////////////////////////////////////////////////
// let allPp = proceduresMapping.filter(p => p.is_principale)
// let allPsUnbinded = proceduresMapping.filter(p => !p.is_principale && p.secondary_procedure_of)
// let bindedSecondary = allPsUnbinded.map(ps => {
//     let secOf = allPp.find(pp => pp.from_sudocu === ps.sudocu_secondary_procedure_of)
//     if(!secOf){
//       console.log(`No match found to link PS: ${ps.id}`)
//       return null
//     }
//     return {id: ps.id, secondary_procedure_of: secOf}
//   }).filter(e => e)
// console.log(`There is ${allPsUnbinded.length} unlinked secondary.`)
//   for (const psUnbinded of allPsUnbinded) {
//     const { data, error } = await supabase.from('procedures').update({secondary_procedure_of: psUnbinded.secondary_procedure_of}).eq('id', psUnbinded.id)
//   }

  await updateProcedureSec(proceduresMapping, configSource, configTraget)

  /// ////////////////////////////////////////
  /// /////////// UPSERT EVENTS //////////////
  /// ////////////////////////////////////////

  currentPage = 1
  pageSize = 10000
  hasMore = true
  let addedBufferEvents = []

  console.log('Starting processing events.')
  while (hasMore) {
    const { data: dataEvents, error: errorEvents } = await supabaseSource.from('sudocu_procedure_events')
      .select('*')
      .order('noserieevenement', { ascending: true })
      .range((currentPage - 1) * pageSize, currentPage * pageSize - 1)
      .limit(pageSize)
    if (errorEvents) { console.log(errorEvents) }
    if (dataEvents && dataEvents.length > 0) {
      // console.log('[EVENTS] Processing page: ', currentPage)
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
        return formattedEvent
      })
      // console.log('Mapped ', currentPage, formattedEvents?.length)
      const { data: insertedEvents, error: errorInsertedEvents } = await supabase.from('doc_frise_events').upsert(formattedEvents, { onConflict: 'from_sudocuh', ignoreDuplicates: true }).select()
      console.log('[EVENTS] Page ',currentPage, ' inserted Events ', insertedEvents?.length)

      addedBufferEvents = [...addedBufferEvents, ...insertedEvents]
      if (errorInsertedEvents) { console.log(errorInsertedEvents) }
      currentPage++
    } else { hasMore = false }
  }

  if (addedBufferEvents.length > 0) {
    const csvNewProcedures = await parser.parse(addedBufferEvents).promise()
    try {
      fs.writeFileSync(`${outputDir}/last_events_added.csv`, csvNewProcedures, { flag: 'w' })
      console.log('Procedures successfully written to file.')
    } catch (error) {
      console.error('Error writing array to file:', error)
    }
  } else {
    console.log('No new procedures. File wont be written in output')
  }
  appendToGithubSummary(`- ${addedBufferEvents.length} nouveaux événements`)
  console.log('End processing events.')

  return true
}

export { sudocuhPlanToDocurba }
