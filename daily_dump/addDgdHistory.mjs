
import { createClient } from '@supabase/supabase-js'
import CONFIG from './pg_secret_config.mjs'

console.log('Current working directory:', process.cwd())

async function main () {
  const supabaseDev = createClient(CONFIG.PG_DEV_CONFIG.url, CONFIG.PG_DEV_CONFIG.admin_key, {
    auth: { persistSession: false },
    db: { schema: 'sudocu' }
  })

  const supabase = createClient(CONFIG.PG_PROD_CONFIG.url, CONFIG.PG_PROD_CONFIG.admin_key, {
    auth: { persistSession: false }
  })

  const pageSize = 1000 // Process 1000 records at a time
  let startIndex = 0
  let hasMore = true

  // eslint-disable-next-line no-unreachable-loop
  while (hasMore) {
    try {
      // Fetch a page of records from dgd
      const { data: dgdRecords, error: selectError } = await supabaseDev
        .from('dgd')
        .select('*')
        .range(startIndex, startIndex + pageSize - 1)

      if (selectError) {
        throw selectError
      }

      if (dgdRecords.length === 0) {
        hasMore = false
        console.log('Finished processing all records')
        break
      }
      const versementsFormat = dgdRecords.map(e => ({
        amount: e.montantdgd,
        year: e.anneedgd,
        category: e.categoriedgd,
        comment: e.commentaire,
        procedure_id: null,
        from_sudocu_procedure_id: e.noserieprocedure,
        from_sudocu: e.noseriedgd
      }))

      console.log('Sample of first 3 versementsFormat items:', versementsFormat.slice(0, 3))
      // Insert records into versements
      const { error: insertVersementsError } = await supabase
        .from('versements')
        .upsert(versementsFormat, { onConflict: 'from_sudocu', ignoreDuplicates: true })

      if (insertVersementsError) {
        throw insertVersementsError
      }

      // // First, get all the relevant procedure IDs in one query
      const { data: procedureMatches, error: procedureError } = await supabase
        .from('procedures')
        .select('id, from_sudocuh')
        .in('from_sudocuh', versementsFormat.map(v => v.from_sudocu_procedure_id))

      if (procedureError) {
        throw procedureError
      }

      // // Create a lookup map for quick access
      const procedureIdMap = new Map(
        procedureMatches.map(p => [p.from_sudocuh, p.id])
      )

      // // Update versementsFormat with procedure_ids
      const versementsWithProcedures = versementsFormat.map(v => ({
        ...v,
        procedure_id: procedureIdMap.get(v.from_sudocu_procedure_id) || null
      }))
      console.log('Sample of first 3 versementsWithProcedures:', versementsWithProcedures.slice(0, 3))

      // Perform the batch upsert
      const { data: insertedVersements, error: insertError } = await supabase
        .from('versements')
        .upsert(versementsWithProcedures, {
          onConflict: 'from_sudocu',
          ignoreDuplicates: false
        })
        .select()

      if (insertError) {
        throw insertError
      }
      console.log(`Successfully processed ${dgdRecords.length} records starting from index ${startIndex}`)
      startIndex += pageSize
    } catch (error) {
      console.error('Error processing records:', error)
      hasMore = false // Stop processing on error
      throw error
    }
  }
}

main().catch(console.error)
