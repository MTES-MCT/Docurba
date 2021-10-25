import Vue from 'vue'

const defaultUser = {
  id: null,
  email: null,
  role: null,
  user_metadata: {}
}

export default ({ $supabase }, inject) => {
  // This is null if user is not logged
  const authUser = $supabase.auth.user()

  const user = Vue.observable(Object.assign({}, defaultUser, authUser))

  if (process.client) {
    $supabase.auth.onAuthStateChange((event, session) => {
      if (session) {
        Object.assign(user, $supabase.auth.user())
      } else {
        Object.assign(user, defaultUser)
      }
    })
  }

  inject('user', user)
}
