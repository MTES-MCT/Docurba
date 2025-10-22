import { createClient } from '@supabase/supabase-js'

export default (_, inject) => {
  const supabaseUrl = process.env.SUPABASE_URL
  const supabaseAdminKey = process.env.SUPABASE_ADMIN_KEY

  inject('supAdmin', createClient(supabaseUrl, supabaseAdminKey, {
    auth: { persistSession: false }
  }))
}
