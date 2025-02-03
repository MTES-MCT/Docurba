/* eslint-disable no-console */
import { createClient } from '@supabase/supabase-js'
import * as fs from 'node:fs'
import path from 'node:path'
import { appendToGithubSummary } from '../common.mjs'

export async function downloadDump(prodConfig, dirname) {
  console.log('⬇️ Téléchargement du dernier dump…')
  const supabase = createClient(prodConfig.url, prodConfig.admin_key, {
    auth: { persistSession: false }
  })
  const { data, errorA } = await supabase.storage
    .from('dump_sudocu')
    .list('', { limit: 1, sortBy: { column: 'created_at', order: 'desc' } })
  if (errorA || data.length < 1) {
    console.error('❌ Impossible de lister les dumps')
    console.error(errorA)
    process.exit(1)
  }

  const latestDumpName = data[0].name
  console.log('Dernier dump:', latestDumpName)
  appendToGithubSummary(`# Dump importé: ${latestDumpName}`)

  const { data: dumpBlob, error } = await supabase.storage
    .from('dump_sudocu')
    .download(latestDumpName)

  if (error) {
    console.error('❌ Échec du téléchargement de', latestDumpName)
    console.error(error)
    process.exit(1)
  }

  fs.writeFileSync(
    path.join(dirname, 'sudocuh_dumps', latestDumpName),
    Buffer.from(await dumpBlob.arrayBuffer())
  )

  console.log('⬇️ Téléchargement terminé.')

  return latestDumpName
}
