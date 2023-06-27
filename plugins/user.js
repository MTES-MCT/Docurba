import Vue from 'vue'

const defaultUser = {
  id: null,
  email: null,
  role: null,
  scope: null,
  user_metadata: {}
}

export default ({ $supabase, route }, inject) => {
  const user = Vue.observable(Object.assign({}, defaultUser))

  async function updateUser () {
    const { data: { session } } = await $supabase.auth.getSession()
    if (session) {
      Object.assign(user, session.user)
      const { data } = await $supabase.from('admin_users_dept').select('role, dept').match({
        user_id: session.user.id,
        user_email: session.user.email
      })
      if (data && data[0]) {
        user.scope = data[0]
      }
    }
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
