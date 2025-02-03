
import { createClient } from '@supabase/supabase-js'
import CONFIG from './pg_secret_config.mjs'

console.log('Current working directory:', process.cwd())

async function main () {
  const supabase = createClient(CONFIG.PG_PROD_CONFIG.url, CONFIG.PG_PROD_CONFIG.admin_key, {
    auth: { persistSession: false }
  })
  try {
    const { data, error } = await supabase.from('procedures').select()
      .is('is_principale', true)
      .not('secondary_procedure_of', 'is', null)
    console.log('data: ', data)
    console.log('error: ', error)
  } catch (error) {
    console.error('Error in batch processing:', error)
  }
}

main().catch(console.error)
