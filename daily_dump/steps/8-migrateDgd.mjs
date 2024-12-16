import { AsyncParser } from '@json2csv/node'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'
import { appendToGithubSummary } from '../common.mjs'

function formatDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}_${month}_${day}`
}

const currentDate = new Date()

const outputDir = `./daily_dump/output/${formatDate(currentDate)}`

async function migrateDgd(configSource, configTarget) {
  console.group('▶️ Starting processing versements.')
  const supabaseDev = createClient(configSource.url, configSource.admin_key, {
    auth: { persistSession: false },
    db: { schema: 'sudocu' }
  })

  const supabase = createClient(configTarget.url, configTarget.admin_key, {
    auth: { persistSession: false }
  })

  const pageSize = 1000
  let startIndex = 0
  let hasMore = true

  const allInsertedVersements = []

  while (hasMore) {
    console.log(`Processing ${pageSize} from ${startIndex}`)
    console.group()
    const { data: dgdRecords, error: selectError } = await supabaseDev
      .from('dgd')
      .select('*')
      .range(startIndex, startIndex + pageSize - 1)

    if (selectError) {
      throw selectError
    }

    if (dgdRecords.length === 0) {
      hasMore = false
      console.groupEnd()
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

    const { data: insertedVersements, error: insertVersementsError } =
      await supabase
        .from('versements')
        .upsert(versementsFormat, {
          onConflict: 'from_sudocu',
          ignoreDuplicates: true
        })
        .select()

    if (insertVersementsError) {
      throw insertVersementsError
    }

    console.log(`${insertedVersements.length} upserted`)
    allInsertedVersements.push(...insertedVersements)

    const { data: procedureMatches, error: procedureError } = await supabase
      .from('procedures')
      .select('id, from_sudocuh')
      .in(
        'from_sudocuh',
        versementsFormat.map(v => v.from_sudocu_procedure_id)
      )

    if (procedureError) {
      throw procedureError
    }

    const procedureIdMap = new Map(
      procedureMatches.map(p => [p.from_sudocuh, p.id])
    )

    const versementsWithProcedures = versementsFormat.map(v => ({
      ...v,
      procedure_id: procedureIdMap.get(v.from_sudocu_procedure_id) || null
    }))

    const { error: insertError } = await supabase
      .from('versements')
      .upsert(versementsWithProcedures, {
        onConflict: 'from_sudocu',
        ignoreDuplicates: false
      })

    if (insertError) {
      throw insertError
    }

    startIndex += pageSize
    console.groupEnd()
  }

  const parser = new AsyncParser()
  if (allInsertedVersements.length > 0) {
    const csvNewVersements = await parser.parse(allInsertedVersements).promise()
    try {
      fs.writeFileSync(
        `${outputDir}/last_versements_added.csv`,
        csvNewVersements,
        { flag: 'w' }
      )
      console.log(
        `${allInsertedVersements.length} versements successfully written to file.`
      )
    } catch (error) {
      console.error('Error writing array to file:', error)
    }
  } else {
    console.log('No new versements. File wont be written in output')
  }
  appendToGithubSummary(`- ${allInsertedVersements.length} nouveaux versements`)
  console.groupEnd()
}

export { migrateDgd }
