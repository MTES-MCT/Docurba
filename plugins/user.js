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

async function handleRedirect ($supabase, event, user, router) {
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
      if (!user.profile.successfully_logged_once) {
        axios({ url: '/api/pipedrive/collectivite_inscrite', method: 'post', data: { userData: { email: user.email } } })
        await $supabase.from('profiles').update({ successfully_logged_once: true }).eq('user_id', user.id)
      }
    }
  }
}

export default async ({ $supabase, app }, inject) => {
  const user = Vue.observable(Object.assign({}, defaultUser))

  async function updateUser (session) {
    // console.log('updateUser', session)

    if (!session) {
      // console.log('get session')
      const { data } = await $supabase.auth.getSession()
      session = data.session

      // console.log('session result', session)
    }

    if (session) {
      Object.assign(user, session.user)

      const { data, error } = await $supabase.from('profiles').select().eq('user_id', session.user.id)
      console.log('profiles', data, ' err: ', error)
      console.log('error: ', error)
      user.profile = data[0]
    }

    // await user.isReady

    return user
  }

  if (process.client) {
    await updateUser()

    $supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('onAuthStateChange', event, session)

      if (session) {
        const user = await updateUser(session)
        handleRedirect($supabase, event, user, app.router)
      } else {
        Object.assign(user, defaultUser)
      }
    })
  }

  inject('user', user)
}
