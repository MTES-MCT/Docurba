import _ from 'lodash'
import { createClient } from '@supabase/supabase-js'
import cliProgress from 'cli-progress'

import departements from '../assets/data/departements-france.json' assert {type: 'json'}
import CONFIG from './pg_secret_config.mjs'

const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', CONFIG.SUPABASE_ADMIN, {
  auth: { persistSession: false }
})

const progressBar = new cliProgress.SingleBar({
  format: 'Progress | {bar} | {percentage}% || {value}/{total} items',
  barCompleteChar: '\u2588',
  barIncompleteChar: '\u2591',
  hideCursor: true
})

// const {data: profiles} = await supabase.from('profiles').select('*')
//   .is('region', null)

// const profilesByDept = _.groupBy(profiles, p => p.departement)

progressBar.start(departements.length, 0)

for(const departement of departements) {
  const deptCode = departement.code_departement.toString().padStart(2, '0')

  await supabase.from('profiles').update({
    region: departement.code_region.toString().padStart(2, '0')
  }).is('region', null).eq('departement', deptCode)

  progressBar.increment()
}
