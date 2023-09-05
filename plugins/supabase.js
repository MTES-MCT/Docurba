import { createClient } from '@supabase/supabase-js'

export default (_, inject) => {
  const supabaseUrl = 'https://ixxbyuandbmplfnqtxyw.supabase.co'
  const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlhdCI6MTYzNDk3NTU3NiwiZXhwIjoxOTUwNTUxNTc2fQ.zvgWeMG3sKSwBKv8uGm5uy82cEyMyEMivQvNIDFhBkA'

  inject('supabase', createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      persistSession: true
    }
  }))
}
