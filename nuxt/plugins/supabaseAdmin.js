import { createClient } from '@supabase/supabase-js'

export default (_, inject) => {
  // const supabaseUrl = 'https://ixxbyuandbmplfnqtxyw.supabase.co'
  const supabaseUrl = 'https://supabase.docurba.beta.gouv.fr'
  const supabaseAdminKey = process.env.SUPABASE_ADMIN_KEY

  inject('supAdmin', createClient(supabaseUrl, supabaseAdminKey, {
    auth: { persistSession: false }
  }))
}
