import fs from 'fs'
import { createClient } from '@supabase/supabase-js'
import CONFIG from '../pg_secret_config.mjs'

function formatDate (date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}_${month}_${day}`
}

const currentDate = new Date()

const outputDir = `./daily_dump/output/${formatDate(currentDate)}`

async function fetchInBatches (supabase, ids, batchSize = 100) {
  let sudocuIdPpPs = []
  let unmatchedIds = []

  for (let i = 0; i < ids.length; i += batchSize) {
    const batch = ids.slice(i, i + batchSize)
    console.log(`Processing batch ${i / batchSize + 1}, IDs ${i + 1} to ${Math.min(i + batchSize, ids.length)}`)

    try {
      const { data, error } = await supabase
        .from('procedure')
        .select('noserieprocedure, noserieprocedureratt')
        .in('noserieprocedure', batch)

      if (error) {
        throw error
      }

      sudocuIdPpPs = sudocuIdPpPs.concat(data)
      console.log(`Batch processed, received ${data.length} records`)

      const matchedIds = new Set(data.map(item => item.noserieprocedure))
      const batchUnmatchedIds = batch.filter(id => !matchedIds.has(id))
      unmatchedIds = unmatchedIds.concat(batchUnmatchedIds)
    } catch (error) {
      console.error('Error processing batch:', error)
    }
  }
  return { sudocuIdPpPs, unmatchedIds }
}

export async function updateProcedureSec (prodProcedures) {
  console.log('In memory prodProcedures: ', prodProcedures[0])

  const supabaseDev = createClient(CONFIG.PG_DEV_CONFIG.url, CONFIG.PG_DEV_CONFIG.admin_key, {
    auth: { persistSession: false },
    db: { schema: 'sudocu' }
  })

  const supabase = createClient(CONFIG.PG_PROD_CONFIG.url, CONFIG.PG_PROD_CONFIG.admin_key, {
    auth: { persistSession: false }
  })

  const allPp = prodProcedures.filter(p => p.is_principale)
  console.log(`Number of principal procedures: ${allPp.length}`)
  const allPsUnbinded = prodProcedures.filter(p => !p.is_principale && !p.sudocu_secondary_procedure_of && !p.secondary_procedure_of && p.from_sudocuh)
  console.log(`Number of sec procedures: ${allPsUnbinded.length}`)

  const idPsUnbinded = allPsUnbinded.map(e => e.from_sudocuh)
  console.log('Total IDs to process:', idPsUnbinded.length)

  try {
    const { sudocuIdPpPs, unmatchedIds } = await fetchInBatches(supabaseDev, idPsUnbinded)
    console.log('Total records fetched:', sudocuIdPpPs.length)
    console.log('Total unmatched IDs:', unmatchedIds.length)
    console.log('Unmatched IDs:', unmatchedIds)
    fs.writeFileSync(`${outputDir}/unmatched_ids_deleted_from_sudocuh.csv`, JSON.stringify(unmatchedIds, null, 2))
    console.log('Unmatched IDs written to unmatched_ids_deleted_from_sudocuh.json')

    const allPsUnbindedEnrich1 = allPsUnbinded.map((ps) => {
      const psMap = sudocuIdPpPs.find(sudoId => sudoId.noserieprocedure === ps.from_sudocuh)
      if (!psMap) {
        console.log('No match found for:', ps)
        return null
      }
      return { id: ps.id, from_sudocuh: ps.from_sudocuh, sudocu_secondary_procedure_of: psMap?.noserieprocedureratt }
    }).filter(e => e)
    console.log('allPsUnbindedEnrich1:', allPsUnbindedEnrich1.slice(0, 5))

    console.log('-------allPsUnbindedEnrich2-----')
    const allPsUnbindedEnrich2 = allPsUnbindedEnrich1.map((ps) => {
      const pp = allPp.find(e => e.from_sudocuh === ps.sudocu_secondary_procedure_of)
      if (!pp) {
        console.log('No match found for:', ps)
        return null
      }
      return { ...ps, secondary_procedure_of: pp.id }
    })
    console.log('allPsUnbindedEnrich2:', allPsUnbindedEnrich2.slice(0, 5))

    console.log(`Starting database (${allPsUnbindedEnrich2.length}) updates...`)
    let updateCount = 0
    let errorCount = 0

    for (const ps of allPsUnbindedEnrich2) {
      if (ps && ps.id && ps.sudocu_secondary_procedure_of && ps.secondary_procedure_of) {
        try {
          const { error } = await supabase
            .from('procedures')
            .update({
              sudocu_secondary_procedure_of: ps.sudocu_secondary_procedure_of,
              secondary_procedure_of: ps.secondary_procedure_of
            })
            .eq('id', ps.id)

          if (error) { throw error }

          updateCount++
          if (updateCount % 100 === 0) {
            console.log(`Updated ${updateCount} procedures`)
          }
        } catch (error) {
          console.error(`Error updating procedure ${ps.id}:`, error)
          errorCount++
        }
      } else {
        console.warn('Skipping update for procedure with incomplete data:', ps)
      }
    }

    console.log('Database update completed.')
    console.log(`Total procedures updated: ${updateCount}`)
    console.log(`Total errors encountered: ${errorCount}`)
  } catch (error) {
    console.error('Error in batch processing:', error)
  }
}
