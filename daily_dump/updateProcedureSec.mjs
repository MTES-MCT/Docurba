import fs from 'fs'
import { createClient } from '@supabase/supabase-js'
import CONFIG from './pg_secret_config.mjs'

console.log('Current working directory:', process.cwd())

const filePath = './daily_dump/output/2024_10_21/mapping_procedures_docurba_sudocuh.json'

function readJsonFile (filePath) {
  try {
    const fileContent = fs.readFileSync(filePath, 'utf8')
    const jsonArray = JSON.parse(fileContent)
    if (!Array.isArray(jsonArray)) {
      throw new TypeError('The file does not contain a JSON array')
    }
    return jsonArray
  } catch (error) {
    console.error('Error reading or parsing the file:', error.message)
    return null
  }
}

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

      // Find unmatched IDs in this batch
      const matchedIds = new Set(data.map(item => item.noserieprocedure))
      const batchUnmatchedIds = batch.filter(id => !matchedIds.has(id))
      unmatchedIds = unmatchedIds.concat(batchUnmatchedIds)
    } catch (error) {
      console.error('Error processing batch:', error)
    }
  }
  return { sudocuIdPpPs, unmatchedIds }
}

async function main () {
  const proceduresMapping = readJsonFile(filePath)
  console.log('In memory proceduresMapping: ', proceduresMapping[0])

  const supabaseDev = createClient(CONFIG.PG_DEV_CONFIG.url, CONFIG.PG_DEV_CONFIG.admin_key, {
    auth: { persistSession: false },
    db: { schema: 'sudocu' }
  })

  const supabase = createClient(CONFIG.PG_PROD_CONFIG.url, CONFIG.PG_PROD_CONFIG.admin_key, {
    auth: { persistSession: false }
  })

  const allPp = proceduresMapping.filter(p => p.is_principale)
  console.log(`Number of principal procedures: ${allPp.length}`)
  const allPsUnbinded = proceduresMapping.filter(p => !p.is_principale && !p.sudocu_secondary_procedure_of && !p.secondary_procedure_of && p.from_sudocuh)
  console.log(`Number of sec procedures: ${allPsUnbinded.length}`)

  const idPsUnbinded = allPsUnbinded.map(e => e.from_sudocuh)
  console.log('Total IDs to process:', idPsUnbinded.length)
  console.log('allPsUnbinded FINDDDD: ', proceduresMapping.find(e => e.noserieprocedure === 194131))

  try {
    const { sudocuIdPpPs, unmatchedIds } = await fetchInBatches(supabaseDev, idPsUnbinded)
    console.log('Total records fetched:', sudocuIdPpPs.length)
    console.log('Total unmatched IDs:', unmatchedIds.length)

    // Output unmatched IDs
    console.log('Unmatched IDs:', unmatchedIds)

    // Optional: Write unmatched IDs to a file
    // fs.writeFileSync('unmatched_ids.json', JSON.stringify(unmatchedIds, null, 2))
    // console.log('Unmatched IDs written to unmatched_ids.json')

    // on met le sudocu_secondary_procedure_of
    const allPsUnbindedEnrich1 = allPsUnbinded.map((ps) => {
      if (ps.from_sudocuh == 194131) {
        console.log('HERE 1: ', ps)
      }
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
      if (ps.sudocu_secondary_procedure_of == 194131) {
        console.log('HERE 2: ', ps)
      }
      if (!pp) {
        console.log('No match found for:', ps)
        return null
      }
      return { ...ps, secondary_procedure_of: pp.id }
    })
    console.log('allPsUnbindedEnrich2:', allPsUnbindedEnrich2.slice(0, 5))
    // Update the database with enriched data
    //
    console.log(`Starting database (${allPsUnbindedEnrich2.length}) updates...`)
    let updateCount = 0
    let errorCount = 0

    for (const ps of allPsUnbindedEnrich2) {
      if (ps && ps.id && ps.sudocu_secondary_procedure_of && ps.secondary_procedure_of) {
        try {
          // const { error } = await supabase
          //   .from('procedures')
          //   .update({
          //     sudocu_secondary_procedure_of: ps.sudocu_secondary_procedure_of,
          //     secondary_procedure_of: ps.secondary_procedure_of
          //   })
          //   .eq('id', ps.id)

          // if (error) { throw error }

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

  // ... [The rest of your main function, including commented out sections, remains unchanged]
}

main().catch(console.error)
