const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

const pipedrive = require('./pipedrive.js')

module.exports = {
  async updateUserRole (userData, role) {
    const { data, error } = await supabase.from('admin_users_dept').update({ role }).match({
      user_email: userData.email,
      dept: userData.dept.code_departement
    }).select()

    if (role === 'ddt' && !error) {
      // Update deal status in Pipedrive.
      const { deals } = pipedrive.findOrganization(userData.dept.code_departement)

      if (deals && deals.length) {
        const deal = deals.find((d) => {
          return d.stage_id === 10 || d.stage_id === 11 || d.stage_id === 12
        })

        if (deal) {
          pipedrive.updateDeal(deal.id, {
            stage_id: 13
          })
        }
      }
    }

    return { data, error }
  }
}
