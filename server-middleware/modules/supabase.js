const { createClient } = require('@supabase/supabase-js')
// DEV
// 'https://drncrjteathtblggsgxi.supabase.co'
// PROD
// 'https://ixxbyuandbmplfnqtxyw.supabase.co'
const supabase = createClient('https://drncrjteathtblggsgxi.supabase.co', process.env.SUPABASE_ADMIN_KEY, {
  auth: { persistSession: false }
})

module.exports = supabase
