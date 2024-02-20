const { createClient } = require('@supabase/supabase-js')
// const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY, {
const supabase = createClient('https://drncrjteathtblggsgxi.supabase.co', process.env.SUPABASE_ADMIN_KEY, {
  auth: { persistSession: false }
})

module.exports = supabase
