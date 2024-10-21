import fs from 'fs'
import { createClient } from '@supabase/supabase-js'
import CONFIG from './pg_secret_config.mjs'

console.log('Current working directory:', process.cwd())

const filePath = './daily_dump/output/2024_10_14/mapping_procedures_docurba_sudocuh.json'

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

const proceduresMapping = readJsonFile(filePath)
console.log('In memory proceduresMapping: ', proceduresMapping[0])

const supabase = createClient(CONFIG.PG_PROD_CONFIG.url, CONFIG.PG_PROD_CONFIG.admin_key, {
  auth: { persistSession: false }
})
/// ///////////////////////////////////////////////////////////////////////////
/// /////////// MAPPING ID PROCEDURES PRINCIPALES / SECONDAIRES  //////////////
/// ///////////////////////////////////////////////////////////////////////////

const allPp = proceduresMapping.filter(p => p.is_principale)
console.log(`Number of principal procedures: ${allPp.length}`)
const allPsUnbinded = proceduresMapping.filter(p => !p.is_principale && p.sudocu_secondary_procedure_of && !p.secondary_procedure_of)
console.log(`Number of sec procedures: ${allPsUnbinded.length}`)

const bindedSecondary = allPsUnbinded.map((ps) => {
  const secOf = allPp.find(pp => pp.from_sudocuh === ps.sudocu_secondary_procedure_of)
  // console.log(`Searching for principal procedure with from_sudocuh: ${ps.sudocu_secondary_procedure_of}`)
  if (!secOf) {
    console.log(`No match found to link PS: ${ps.id}`)
    return null
  }
  return { id: ps.id, secondary_procedure_of: secOf }
}).filter(e => e)
console.log(`There is ${bindedSecondary.length} unlinked secondary.`)
// for (const psUnbinded of allPsUnbinded) {
//   const { data, error } = await supabase.from('procedures').update({ secondary_procedure_of: psUnbinded.secondary_procedure_of }).eq('id', psUnbinded.id)
// }
