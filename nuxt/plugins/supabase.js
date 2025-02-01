import { createClient } from '@supabase/supabase-js'
// import { PG_DEV_CONFIG, PG_PROD_CONFIG } from '@/database/pg_secret_config.json'

export default (_, inject) => {
  // const supabaseUrl = 'https://ixxbyuandbmplfnqtxyw.supabase.co'
  const supabaseUrl = 'https://supabase.docurba.beta.gouv.fr'
  const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlhdCI6MTYzNDk3NTU3NiwiZXhwIjoxOTUwNTUxNTc2fQ.zvgWeMG3sKSwBKv8uGm5uy82cEyMyEMivQvNIDFhBkA'

  inject('supabase', createClient(supabaseUrl, supabaseAnonKey))
  // const DB_CONFIG = PG_DEV_CONFIG
  // console.log(`Running on ${DB_CONFIG.env === 'dev' ? 'Dev' : 'Prod'} database instance.`)
  // console.log('Need run with PG_PROD_CONFIG for deploy: ', PG_PROD_CONFIG)
  // inject('supabase', createClient(`https://${DB_CONFIG.host}`, DB_CONFIG.anon_key))
}
