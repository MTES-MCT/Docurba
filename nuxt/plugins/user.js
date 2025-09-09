import Vue from 'vue'
import axios from 'axios'

const defaultUser = {
  id: null,
  email: null,
  role: null,
  profile: {},
  scope: null,
  isReady: false,
  user_metadata: {}
}

function handleRedirect ($supabase, event, user, router) {
  // console.log('handleRedirect: ', event, user)
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

    if (user.profile.side === 'collectivite') {
      axios({
        url: '/api/pipedrive/collectivite_inscrite',
        method: 'post',
        data: { userData: { email: user.email } }
      })
    }
  }
}

export default async ({ $supabase, app }, inject) => {
  const user = Vue.observable(Object.assign({}, defaultUser))

  async function updateUser (session, retry = true) {
    // console.log('updateUser', session)

    if (!session) {
      // console.log('get session')
      const { data } = await $supabase.auth.getSession()
      session = data.session

      // console.log('session result', session)
    }

    if (session) {
      // console.log('using session')
      Object.assign(user, session.user)

      user.isReady = new Promise((resolve, reject) => {
        // console.log('session.user.id', session.user.id)

        $supabase.from('profiles').select('*').eq('user_id', session.user.id)
          .then(async ({ data, error }) => {
          // console.log('profiles', data)
            if (data[0]) {
              user.profile = data[0]

              if (!user.profile.successfully_logged_once) {
                await $supabase.from('profiles')
                  .update({
                    successfully_logged_once: true
                  }).eq('user_id', session.user.id)
              }

              resolve(true)
            } else if (retry) {
              setTimeout(async () => {
                await updateUser(session, false)
              }, 200)

              resolve(false)
            }
          })
      })
    }

    await user.isReady
    // console.log('user ready')

    return user
  }

  if (process.client) {
    await updateUser(null, false)

    let currentSession = null

    $supabase.auth.onAuthStateChange(async (event, session) => {
      // console.log('onAuthStateChange', event, session)

      if (session) {
        // console.log('update user with session')
        if (event === 'INITIAL_SESSION ' || !currentSession) {
          const user = await updateUser(session)
          // console.log('user updated')
          handleRedirect($supabase, event, user, app.router)
        }

        currentSession = session
      } else {
        currentSession = null
        Object.assign(user, defaultUser)
      }
    })
  }

  inject('user', user)
}
