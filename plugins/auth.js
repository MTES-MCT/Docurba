export default ({ $supabase, $user }, inject) => {
  inject('auth', {
    async getDeptAccess () {
      const { data: adminAccess } = await $supabase.from('admin_users_dept').select('role, dept').match({
        user_id: $user.id,
        user_email: $user.email,
        role: 'ddt'
      })

      return adminAccess[0] || null
    },
    async getRegionAccess () {
      const { data: adminAccess } = await $supabase.from('admin_users_region').select('role, region').match({
        user_id: $user.id,
        user_email: $user.email,
        role: 'admin'
      })

      return adminAccess[0] || null
    },
    signUp (userData) {
      return $supabase.auth.signUp({
        email: userData.email,
        password: userData.password
      }, {
        data: {
          firstname: userData.firstname,
          lastname: userData.lastname
        }
      })
    },
    signIn (userData) {
      return $supabase.auth.signIn({
        email: userData.email,
        password: userData.password
      })
    }
  })
}
