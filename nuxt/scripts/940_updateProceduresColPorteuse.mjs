import fs from 'fs'
import { parseArgs } from 'node:util'
import { createClient } from '@supabase/supabase-js'
import cliProgress from 'cli-progress'
import { AsyncParser } from '@json2csv/node'

const { values: { write } } = parseArgs({
  options: {
    write: {
      type: 'boolean', default: false
    }
  },
  strict: true
})

if (write) {
  console.warn('La base de données sera éditée')
}

function convertArrayToCsv (dataArray, outputFile) {
  try {
    const fields = Object.keys(dataArray[0])
    const opts = { fields }

    const asyncParser = new AsyncParser(opts)
    const outputStream = fs.createWriteStream(outputFile)

    asyncParser.parse(dataArray).pipe(outputStream)

    console.log(`CSV file created successfully: ${outputFile}`)
  } catch (err) {
    console.error('Error converting array to CSV:', err)
  }
}

const progressBar = new cliProgress.SingleBar({
  format: 'Progress | {bar} | {percentage}% || {value}/{total} items',
  barCompleteChar: '\u2588',
  barIncompleteChar: '\u2591',
  hideCursor: true
})

const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.PROD_SUPABASE_ADMIN_KEY, {
  auth: { persistSession: false }
})

const { data: procedures, error } = await supabase.from('procedures').select('*, procedures_perimetres(*)')
  // .eq and .limit here are just for testing
  // .eq('id', '1e7f4571-3fae-4087-a56b-730cf32e5258')
  // .is('from_sudocuh', null)
  .not('owner_id', 'is', null)
  // .eq('is_principale', true)
  .eq('archived', false)
  // .limit(1)

console.log(error)
console.log(procedures.length)

const needToChange = {
  "Sudocuh pas d'accord": 0,
  'PLUi porté par commune': 0,
  'PLU porté par interco au lieu de commune': 0,
  'PLU porté par commune au lieu de interco': 0
}

const procToChange = []

progressBar.start(procedures.length, 0)

for (let index = 0; index < procedures.length; index++) {
  // console.log(`${index}/${procedures.length}`)
  progressBar.update(index + 1)

  const procedure = procedures[index]
  // We filter COMD to avoid confusion between PLU on COMD and PLUi.
  const perim = procedure.procedures_perimetres.filter(p => p.collectivite_type === 'COM')
  // console.log(perim)

  // If we have a PLUi not managed by a groupement we need to update it to the correct group.
  if (perim.length > 1 && procedure.collectivite_porteuse_id.length < 6) {
    const res = await fetch(`https://nuxt3.docurba.incubateur.net/api/geo/communes?code=${perim[0].collectivite_code}`)
    const communes = await res.json()
    const commune = communes[0]

    // console.log('PLUi porté par commune')
    needToChange['PLUi porté par commune'] += 1
    if (write) {
      await supabase.from('procedures').update({
        collectivite_porteuse_id: commune.intercommunaliteCode
      }).eq('id', procedure.id)
    }
  }

  if (perim.length === 1) {
    const res = await fetch(`https://nuxt3.docurba.incubateur.net/api/geo/communes?code=${perim[0].collectivite_code}`)
    const communes = await res.json()
    const commune = communes[0]

    // Commune a competence in Banatic so code should be itself.
    if (commune.competencePLU && procedure.collectivite_porteuse_id !== commune.code) {
      // console.log('PLU porté par interco au lieu de commune')
      needToChange['PLU porté par interco au lieu de commune'] += 1

      if (procedure.from_sudocuh) {
        needToChange["Sudocuh pas d'accord"] += 1
        procToChange.push({
          id: procedure.id,
          url: `https://dev.docurba.beta.gouv.fr/frise/${procedure.id}`,
          isPrincipale: procedure.is_principale,
          sudocuh: procedure.collectivite_porteuse_id,
          banatic: commune.code
        })
      } else if (write) {
        await supabase.from('procedures').update({
          collectivite_porteuse_id: commune.code
        }).eq('id', procedure.id)
      }
    }

    // Commune does not have competence so code should be its group.
    if (!commune.competencePLU && procedure.collectivite_porteuse_id.length < 6) {
      // console.log('PLU porté par commune au lieu de interco')
      needToChange['PLU porté par commune au lieu de interco'] += 1
      if (write) {
        await supabase.from('procedures').update({
          collectivite_porteuse_id: commune.intercommunaliteCode
        }).eq('id', procedure.id)
      }
    }
  }
}

progressBar.stop()

await convertArrayToCsv(procToChange, 'ColPorteuse.csv')

console.log(needToChange)
