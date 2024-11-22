/* eslint-disable no-console */
import { createClient } from '@supabase/supabase-js'
import * as fs from 'node:fs'
import path from 'node:path'

export async function downloadDump(prodConfig, dumpFilename, dirname) {
  console.log('⬇️ Téléchargement du dump…')
  const supabase = createClient(prodConfig.url, prodConfig.admin_key, {
    auth: { persistSession: false }
  })
  const { data: dumpBlob, error } = await supabase.storage
    .from('dump_sudocu')
    .download(dumpFilename)

  if (error) {
    console.error('❌ Échec du téléchargement de', dumpFilename)
    console.error(error)
    process.exit(1)
  }

  fs.writeFileSync(
    path.join(dirname, 'sudocuh_dumps', dumpFilename),
    Buffer.from(await dumpBlob.arrayBuffer())
  )
}
