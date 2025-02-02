import { omit } from 'lodash'

export default ({ $supabase, $user }, inject) => {
  inject('auth', {
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
        const { data: profile, error: errorInsertProfile } = await $supabase.from('profiles').insert({
          ...sanitizedUserData, side: 'etat', user_id: user.id
        }).select()

        if (errorInsertProfile) { throw errorInsertProfile }

        const newProfile = profile[0]

        if (newProfile.poste === 'ddt') {
          await $supabase.from('github_ref_roles').insert([{
            role: 'user',
            ref: `dept-${newProfile.departement}`,
            user_id: user.id
          }])
        }

        return { user, profile: newProfile }
      } catch (error) {
        if (error.message === 'User already registered') {
          throw new Error('Cet email est déjà enregistré. Cliquez plutôt sur “J’ai déjà un compte” ou réinitialisez votre mot de passe si vous l’avez oublié.')
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
