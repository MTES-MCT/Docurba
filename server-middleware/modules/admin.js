const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

const pipedrive = require('./pipedrive.js')
const sendgrid = require('./sendgrid.js')

module.exports = {
  async updateUserRole (userData, role) {
    const { data, error } = await supabase.from('github_ref_roles').update({ role }).match({
      user_id: userData.id,
      ref: `dept-${userData.departement}`
    }).select()

    // eslint-disable-next-line no-console
    console.log('updateUserRole', data, error)

    if (role === 'ddt' && !error) {
      // TODO: Send email Validation de compte.
      // d-939bd4723dd04edcad17e6584b7641f3
      // {firstname, dept}

      sendgrid.sendEmail({
        to: userData.email,
        template_id: 'd-06e865fdc30d42a398fdc6bc532deb82',
        dynamic_template_data: {
          firstname: userData.firstname || '',
          dept: userData.departement
        }
      })

      // Update deal status in Pipedrive.
      const { deals } = pipedrive.findOrganization(userData.departement)

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
  },
  // not used and obselete
  async getUserAdminRoles (userId) {
    const { data: deptRoles } = await supabase
      .from('admin_users_dept')
      .select('*')
      .match({ user_id: userId, role: 'ddt' })

    const { data: regionRoles } = await supabase
      .from('admin_users_region')
      .select('*')
      .match({ user_id: userId, role: 'admin' })

    return { deptRoles, regionRoles }
  }
}
