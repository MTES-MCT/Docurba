import Vue from 'vue'

const defaultUser = {
  id: null,
  email: null,
  role: null,
  profile: {},
  scope: null,
  isReady: false,
  user_metadata: {}
}

function handleRedirect (event, user, router) {
  if (event === 'SIGNED_IN') {
    if (user.profile.poste === 'dreal') {
      function trameRef (user) {
        const scopes = { ddt: 'dept', dreal: 'region' }
        const poste = user.profile.poste
        const code = poste === 'ddt' ? user.profile.departement : user.profile.region

        return `${scopes[poste]}-${code}`
      }
      router.push({ name: 'trames-githubRef', params: { githubRef: trameRef(user) } })
    } else if (user.profile.poste === 'ddt') {
      router.push({ name: 'ddt-departement-collectivites', params: { departement: user.profile.departement } })
    }
  }
}

export default ({ $supabase, app }, inject) => {
  const user = Vue.observable(Object.assign({}, defaultUser))

  async function updateUser () {
    const { data: { session } } = await $supabase.auth.getSession()
    if (session) {
      Object.assign(user, session.user)

      user.isReady = new Promise((resolve, reject) => {
        Promise.all([
          $supabase.from('profiles').select().eq('user_id', session.user.id),
          $supabase.from('admin_users_dept').select('role, dept').match({
            user_id: session.user.id,
            user_email: session.user.email
          })
        ]).then(([userProfile, userAdminRefs]) => {
          if (userProfile?.data?.[0]) { user.profile = userProfile.data[0] }
          if (userAdminRefs?.data?.[0]) { user.scope = userAdminRefs.data[0] }
          resolve(true)
        })
      })
    }
    return user
  }

  if (process.client) {
    updateUser()

    $supabase.auth.onAuthStateChange(async (event, session) => {
      if (session) {
        const user = await updateUser()
        handleRedirect(event, user, app.router)
      } else {
        Object.assign(user, defaultUser)
      }
    })
  }

  inject('user', user)
}
