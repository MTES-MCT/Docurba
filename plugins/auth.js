export default ({ $supabase }, inject) => {
  inject('auth', {
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
