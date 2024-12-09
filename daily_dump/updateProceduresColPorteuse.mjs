import { createClient } from '@supabase/supabase-js'
import cliProgress from 'cli-progress'

import CONFIG from './pg_secret_config.mjs'

const progressBar = new cliProgress.SingleBar({
  format: 'Progress | {bar} | {percentage}% || {value}/{total} items',
  barCompleteChar: '\u2588',
  barIncompleteChar: '\u2591',
  hideCursor: true
})

const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', CONFIG.SUPABASE_ADMIN, {
  auth: { persistSession: false }
})

const { data: procedures } = await supabase.from('procedures').select('*, procedures_perimetres(*)')
  // .eq and .limit here are just for testing
  // .eq('id', '1e7f4571-3fae-4087-a56b-730cf32e5258')
  .is('from_sudocuh', null)
  // .limit(1)

console.log(procedures.length)

const needToChange = {
  'PLUi porté par commune': 0,
  'PLU porté par interco au lieu de commune': 0,
  'PLU porté par commune au lieu de interco': 0
}

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
    const commune = await res.json()

    // console.log('PLUi porté par commune')
    needToChange['PLUi porté par commune'] += 1
    // await supabase.update({
    //   collectivite_porteuse_id: commune.intercommunaliteCode
    // }).eq('id', procedure.id)
  }

  if (perim.length === 1) {
    const res = await fetch(`https://nuxt3.docurba.incubateur.net/api/geo/communes?code=${perim[0].collectivite_code}`)
    const commune = await res.json()

    // Commune a competence in Banatic so code should be itself.
    if (commune.competencePLU && procedure.collectivite_porteuse_id !== commune.code) {
      // console.log('PLU porté par interco au lieu de commune')
      needToChange['PLU porté par interco au lieu de commune'] += 1
      // await supabase.update({
      //   collectivite_porteuse_id: commune.code
      // }).eq('id', procedure.id)
    }

    // Commune does not have competence so code should be its group.
    if (!commune.competencePLU && procedure.collectivite_porteuse_id.length < 6) {
      // console.log('PLU porté par commune au lieu de interco')
      needToChange['PLU porté par commune au lieu de interco'] += 1
      console.log(procedure.id)
      // await supabase.update({
      //   collectivite_porteuse_id: commune.intercommunaliteCode
      // }).eq('id', procedure.id)
    }
  }
}

progressBar.stop()
console.log(needToChange)
