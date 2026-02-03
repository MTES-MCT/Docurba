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
  if (event === 'SIGNED_IN') {
    switch (user.profile.side) {
      case 'etat':
        if (user.profile.poste === 'dreal') {
          function trameRef (user) {
            const scopes = { ddt: 'dept', dreal: 'region' }
            const { poste } = user.profile
            const code = poste === 'ddt' ? user.profile.departement : user.profile.region
            return `${scopes[poste]}-${code}`
          }

          router.push({ name: 'trames-githubRef', params: { githubRef: trameRef(user) } })
        } else if (user.profile.poste === 'ddt') {
          router.push({ name: 'ddt-departement-collectivites', params: { departement: user.profile.departement } })
        }
        break

      case 'ppa':
        router.push({ name: 'ddt-departement-collectivites', params: { departement: user.profile.departement } })
        break

      case 'collectivite':
        axios({
          url: '/api/pipedrive/collectivite_inscrite',
          method: 'post',
          data: { userData: { email: user.email } }
        })
        break
      default:
        break
    }
  }
}

// Mandatory for SonarQube
// eslint-disable-next-line import/no-anonymous-default-export
export default async ({ $supabase, app }, inject) => {
  let user = Vue.observable({ ...defaultUser })

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

  // Rights management
  const userRights = {
    canViewDDTLayout () {
      return ['etat', 'ppa'].includes(this.profile.side)
    },
    canViewSectionCollectivites ({ departement = null }) {
      if (this.profile.is_admin) {
        return true
      }

      if (this.profile.poste === 'ddt') {
        return this.profile.departement === departement
      } else if (this.profile.side === 'ppa') {
        return this.profile.departements.includes(departement)
      }
    },
    canViewSectionProcedures ({ departement = null }) {
      if (this.profile.is_admin) {
        return true
      }

      if (this.profile.poste === 'ddt') {
        return this.profile.departement === departement
      } else if (this.profile.side === 'ppa') {
        return this.profile.departements.includes(departement)
      }
    },
    canViewSectionTramesPAC () {
      return this.profile.side === 'etat'
    },
    canViewSectionPAC () {
      return this.profile.side === 'etat' && this.profile.poste === 'ddt'
    },
    canCreateProcedure ({ collectivite = null, departement = null }) {
      if (this.profile.is_admin) {
        return true
      }

      switch (this.profile.side) {
        case 'etat': {
          return this.profile.departement === (collectivite?.departementCode || departement)
        }

        case 'collectivite': {
          return (
            this.profile.collectivite_id === collectivite?.code ||
            this.profile.collectivite_id === collectivite?.intercommunaliteCode
          )
        }

        default: {
          return false
        }
      }
    },
    canUpdateProcedure (procedure) {
      return procedure.owner_id === this.id || this.profile.poste === 'ddt'
    },
    canDeleteProcedure () {
      return this.profile.side !== 'ppa'
    },
    canViewMultipleDepartements () {
      return this.profile.side === 'ppa' || this.profile.is_admin
    },
    canViewEnquete () {
      return (this.profile.side === 'etat' && this.profile.poste === 'ddt') || this.profile.is_admin
    }
  }

  user = Object.assign(user, userRights)

  inject('user', user)
}
