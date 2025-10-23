import { createClient } from '@supabase/supabase-js'
// import { PG_DEV_CONFIG, PG_PROD_CONFIG } from '@/database/pg_secret_config.json'

export default (_, inject) => {
  const supabaseUrl = process.env.SUPABASE_URL
  const supabaseAnonKey = process.env.SUPABASE_ANON_KEY

  inject('supabase', createClient(supabaseUrl, supabaseAnonKey))
  // const DB_CONFIG = PG_DEV_CONFIG
  // console.log(`Running on ${DB_CONFIG.env === 'dev' ? 'Dev' : 'Prod'} database instance.`)
  // console.log('Need run with PG_PROD_CONFIG for deploy: ', PG_PROD_CONFIG)
  // inject('supabase', createClient(`https://${DB_CONFIG.host}`, DB_CONFIG.anon_key))
}
