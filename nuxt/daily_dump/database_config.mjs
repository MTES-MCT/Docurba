export default {
  PG_DEV_CONFIG: {
    env: 'dev',
    url: process.env.DEV_SUPABASE_URL,
    host: process.env.DEV_SUPABASE_HOST,
    port: process.env.DEV_SUPABASE_PORT,
    database: process.env.DEV_SUPABASE_DATABASE
  },
  PG_PROD_CONFIG: {
    env: 'prod',
    url: process.env.PROD_SUPABASE_URL,
    host: process.env.PROD_SUPABASE_HOST,
    port: process.env.PROD_SUPABASE_PORT,
    database: process.env.PROD_SUPABASE_DATABASE
  }
}
