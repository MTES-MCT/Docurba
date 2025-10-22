import { createBrowserClient, createServerClient, parseCookieHeader, serializeCookieHeader } from '@supabase/ssr'
// import { PG_DEV_CONFIG, PG_PROD_CONFIG } from '@/database/pg_secret_config.json'

export default ({ req, res }, inject) => {
  // const supabaseUrl = 'https://ixxbyuandbmplfnqtxyw.supabase.co'
  const supabaseUrl = 'https://supabase.docurba.beta.gouv.fr'
  const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4eGJ5dWFuZGJtcGxmbnF0eHl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA4NTA4ODMsImV4cCI6MjA1NjQyNjg4M30.UDomMAiu5MZrQ8NqfDBfSrXRL_O3dSIrP8pyGy6QTAc'

  if (process.client) {
    inject('supabase', createBrowserClient(supabaseUrl, supabaseAnonKey))
  } else {
    inject('supabase', createServerClient(supabaseUrl, supabaseAnonKey, {
      cookies: {
        getAll () {
          return parseCookieHeader(req.headers.cookie ?? '')
        },
        setAll (cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) =>
            res.appendHeader('Set-Cookie', serializeCookieHeader(name, value, options))
          )
        }
      }
    }))
  }
  // const DB_CONFIG = PG_DEV_CONFIG
  // console.log(`Running on ${DB_CONFIG.env === 'dev' ? 'Dev' : 'Prod'} database instance.`)
  // console.log('Need run with PG_PROD_CONFIG for deploy: ', PG_PROD_CONFIG)
  // inject('supabase', createClient(`https://${DB_CONFIG.host}`, DB_CONFIG.anon_key))
}
