import Vue from 'vue'

const defaultUser = {
  id: null,
  email: null,
  role: null,
  user_metadata: {}
}

export default ({ $supabase, route }, inject) => {
  const user = Vue.observable(Object.assign({}, defaultUser))

  async function updateUser () {
    const { data: { session } } = await $supabase.auth.getSession()
    Object.assign(user, session.user)
  }

  if (process.client) {
    updateUser()

    $supabase.auth.onAuthStateChange((event, session) => {
      if (session) {
        updateUser()
      } else {
        Object.assign(user, defaultUser)
      }
    })
  }

  inject('user', user)
}
