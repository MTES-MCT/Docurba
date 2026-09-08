export default ({ $supabase, $user }, inject) => {
  inject('auth', {
    async signIn ({ email, password }) {
      const { data: { user }, error } = await $supabase.auth.signInWithPassword({
        email,
        password
      })

      return { user, error }
    }
  })
}
