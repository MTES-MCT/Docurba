import { createClient } from '@supabase/supabase-js'

export default (_, inject) => {
  const supabaseUrl = 'https://ixxbyuandbmplfnqtxyw.supabase.co'
  const supabaseAdminKey = process.env.SUPABASE_ADMIN_KEY

  inject('supAdmin', createClient(supabaseUrl, supabaseAdminKey))
}
