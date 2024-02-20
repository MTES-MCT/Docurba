import { createClient } from '@supabase/supabase-js'
// import { PG_DEV_CONFIG, PG_PROD_CONFIG } from '@/database/pg_secret_config.json'

export default (_, inject) => {
  // const supabaseUrl = 'https://ixxbyuandbmplfnqtxyw.supabase.co'
  const supabaseUrl = 'https://drncrjteathtblggsgxi.supabase.co'
  // const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlhdCI6MTYzNDk3NTU3NiwiZXhwIjoxOTUwNTUxNTc2fQ.zvgWeMG3sKSwBKv8uGm5uy82cEyMyEMivQvNIDFhBkA'
  const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRybmNyanRlYXRodGJsZ2dzZ3hpIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTA4MTI3NDQsImV4cCI6MjAwNjM4ODc0NH0.YGoImCMvK_USyrVd1XMWxCmTLcCYNEDva5sPqLKqgwM'

  inject('supabase', createClient(supabaseUrl, supabaseAnonKey))
  // const DB_CONFIG = PG_DEV_CONFIG
  // console.log(`Running on ${DB_CONFIG.env === 'dev' ? 'Dev' : 'Prod'} database instance.`)
  // console.log('Need run with PG_PROD_CONFIG for deploy: ', PG_PROD_CONFIG)
  // inject('supabase', createClient(`https://${DB_CONFIG.host}`, DB_CONFIG.anon_key))
}
