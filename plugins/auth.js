export default ({ $supabase, $user }, inject) => {
  inject('auth', {
    // multiple allow you to get all region access instead of the first
    async getDeptAccess (multiple) {
      const { data: adminAccess } = await $supabase.from('admin_users_dept').select('role, dept').match({
        user_id: $user.id,
        user_email: $user.email,
        role: 'ddt'
      })

      if (multiple) {
        return adminAccess
      } else { return adminAccess[0] || null }
    },
    async getRegionAccess (multiple) {
      const { data: adminAccess } = await $supabase.from('admin_users_region').select('role, region').match({
        user_id: $user.id,
        user_email: $user.email,
        role: 'admin'
      })

      if (multiple) {
        return adminAccess
      } else { return adminAccess[0] || null }
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
    async signIn (userData) {
      const { data: { user }, error } = await $supabase.auth.signInWithPassword({
        email: userData.email,
        password: userData.password
      })

      return { user, error }
    }
  })
}
