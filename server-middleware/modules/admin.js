const supabase = require('./supabase.js')
const pipedrive = require('./pipedrive.js')
const sendgrid = require('./sendgrid.js')

const regions = require('./Data/INSEE/regions.json')

module.exports = {
  async updateUserRole (userData, role) {
    const { data, error } = await supabase.from('github_ref_roles').update({ role }).match({
      user_id: userData.user_id,
      ref: `dept-${userData.departement}`
    }).select()

    // eslint-disable-next-line no-console
    console.log('updateUserRole', data, error)

    if ((role === 'ddt' || role === 'dreal') && !error) {
      const { data: profiles } = await supabase.from('profiles').select('firstname, lastname, departement, region')
      const profile = profiles[0]
      const { firstname, lastname, departement, region } = profile
      const regionName = regions.find(r => r.code === region)

      sendgrid.sendEmail({
        to: userData.email,
        template_id: role === 'ddt' ? 'd-939bd4723dd04edcad17e6584b7641f3' : 'd-3d9f4b96863d4c6e8d4c9489f6d8eb6e',
        dynamic_template_data: {
          firstname,
          lastname,
          departement: departement || '',
          regionName: regionName || '',
          region: (+region).toString()
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
