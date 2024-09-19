
import fs from 'fs'
import { createClient } from '@supabase/supabase-js'
import DOCUMENTS_TYPES from './miscs/documentTypes.mjs'
import PROCEDURES_TYPES from './miscs/proceduresTypes.mjs'

async function updateProcedureSec (configSource, configTraget) {
  const supabaseSource = createClient(configSource.url, configSource.admin_key, {
    auth: { persistSession: false }
  })

  const supabase = createClient(configTraget.url, configTraget.admin_key, {
    auth: { persistSession: false }
  })

  // const pageSize = 10000
  // let currentPage = 1
  // let hasMore = true

  // let allProceduresSecs = []
  // currentPage = 1
  // hasMore = true

  // console.log('Starting processing procedures secondaires.')
  // while (hasMore) {
  //   const { data: dataProceduresSecs, error: errorProceduresSecs } = await supabaseSource.from('sudocu_procedure_plan')
  //     .select('*')
  //     .in('noserietypeprocedure', PROCEDURES_TYPES.filter(e => !e.siprocedureprincipale).map(e => e.noserietypeprocedure))
  //     .order('noserieprocedure', { ascending: true })
  //     .range((currentPage - 1) * pageSize, currentPage * pageSize - 1)
  //     .limit(pageSize)
  //   if (errorProceduresSecs) { console.log(errorProceduresSecs) }
  //   if (dataProceduresSecs && dataProceduresSecs.length > 0) {
  //     console.log('[PROC. SEC.] Processing page: ', currentPage)
  //     const formattedProcedures = dataProceduresSecs?.map((procedure) => {
  //       return {
  //         from_sudocuh: procedure.noserieprocedure,
  //         secondary_procedure_of: null,
  //         sudocu_secondary_procedure_of: procedure.noserieprocedureatt
  //       }
  //     })

  //     allProceduresSecs = [...allProceduresSecs, ...formattedProcedures]
  //     currentPage++
  //   } else { hasMore = false }
  // }

  // console.log(`End processing for procedures secondaires: ${allProceduresSecs.length} : allProceduresSecs[Ø]: ${allProceduresSecs[0]}`)

  const { data: docurbaToUpdatePs, error: errordocurbaToUpdatePs } = await supabase.from('procedures')
    .select('*', { count: 'exact', head: true }).is('is_principale', false)// .is('sudocu_secondary_procedure_of', null)
  if (errordocurbaToUpdatePs) { console.log(errordocurbaToUpdatePs) }
  console.log('docurbaToUpdatePs: ', docurbaToUpdatePs)
}

export { updateProcedureSec }
