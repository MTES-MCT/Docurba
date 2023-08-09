import { omit } from 'lodash'

export default ({ $supabase, $user }, inject) => {
  inject('auth', {
    async getRefsRoles () {
      // console.log('userId', $user.id)

      const { data: roles } = await $supabase.from('github_ref_roles').select('*')
        .match({
          user_id: $user.id,
          role: 'admin'
        })

      return roles
    },
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
    async signUpStateAgent (userData) {
      try {
        const { data: { user }, error: signupError } = await $supabase.auth.signUp({
          email: userData.email,
          password: userData.password
        }, {
          data: {
            firstname: userData.firstname,
            lastname: userData.lastname
          }
        })

        if (signupError) { throw signupError }
        const sanitizedUserData = omit(userData, ['password'])
        const { data: profile, error: errorInsertProfile } = await $supabase.from('profiles').insert({ ...sanitizedUserData, side: 'etat', user_id: user.id }).select()
        if (errorInsertProfile) { throw errorInsertProfile }
        const newProfile = profile[0]
        if (newProfile.poste === 'ddt') {
          await $supabase.from('github_ref_roles').insert([{
            role: 'user',
            ref: `dept-${newProfile.departement}`,
            user_id: user.id
          }])
        }

        return { user, profile }
      } catch (error) {
        if (error.message === 'User already registered') {
          throw new Error('Cet e-mail est déjà enregistré. Vous pouvez réinitialiser votre mot de passe si vous l\'avez oublié.')
        } else {
          throw error
        }
      }
    },
    async signIn ({ email, password }) {
      const { data: { user }, error } = await $supabase.auth.signInWithPassword({
        email,
        password
      })

      return { user, error }
    }
  })
}
