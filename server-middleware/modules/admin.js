const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

module.exports = {
  async updateUserRole (userData, role) {
    const { data, error } = await supabase.from('admin_users_dept').update({ role }).match({
      user_email: userData.email,
      dept: userData.dept.code_departement
    })

    if (role === 'ddt' && !error) {
      // Update deal status in Pipedrive.
    }

    return { data, erro }
  }
}
