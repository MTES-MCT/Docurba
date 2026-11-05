import { orderBy } from 'lodash'

// interface User {
//   accessToken: string
//   admin: boolean
//   departmentCode: string | null
//   departmentCodes: string[]
//   email: string
//   firstname: string
//   id: string
//   lastname: string
//   regionCode: string | null
//   scope: UserScope | null
//   territorialAuthorityCode: string | null
// }
// enum UserScope {
//   State = 'state',
//   Region = 'region',
//   Department = 'department',
//   TerritorialAuthority = 'territorial-authority',
// }

export const UserScope = {
  State: 'state',
  Region: 'region',
  Department: 'department',
  TerritorialAuthority: 'territorial-authority',
}

export const state = () => ({
  initialized: false,
  user: null,
})

export const getters = {
  accessDepartmentTerritorialAuthorities(state, getters) {
    return (departmentCode) => getters.signedIn && (
      state.user.admin || state.user.departmentCodes.includes(departmentCode)
    )
  },
  accessProcedureCreation(state, getters) {
    return ({ departmentCode, intercommunalityCode, territorialAuthorityCode }) =>
      getters.signedIn
        ? state.user.admin
          ? true
          : state.user.role === UserScope.TerritorialAuthority
            ? [territorialAuthorityCode, intercommunalityCode]
              .filter(Boolean)
              .includes(state.user.territorialAuthorityCode)
            : state.user.departmentCodes.includes(departmentCode)
        : false
  },
  signedIn(state) {
    return !!state.user
  },
  user(state) {
    return state.user
  },
}

export const mutations = {
  setInitialized(state, initialized) {
    state.initialized = initialized
  },
  setUser(state, user) {
    state.user = user
  },
}

export const actions = {
  async init({ commit, dispatch, rootGetters, state }) {
    if (state.initialized) {
      return false
    }

    const { data, error } = await rootGetters['api/auth'].getSession()

    if (error || !data.session) {
      commit('setInitialized', true)

      return false
    }
    try {
      const userUpdated = await dispatch('updateUser', {
        accessToken: data.session.access_token,
        id: data.session.user.id,
      })
      commit('setInitialized', true)

      return userUpdated
    } catch {
      commit('setInitialized', true)

      return false
    }
  },
  async signIn({ dispatch, rootGetters }, { email, password }) {
    const { data, error } = await rootGetters['api/auth'].signInWithPassword({
      email,
      password,
    })

    if (error) {
      throw error
    }

    return dispatch('updateUser', {
      accessToken: data.session.access_token,
      id: data.user.id,
    })
  },
  async signOut({ commit, rootGetters }) {
    const { error } = await rootGetters['api/auth'].signOut()

    if (error) {
      throw error
    }

    commit('setUser', null)

    return true
  },
  async updateUser({ commit, rootGetters }, { accessToken, id }) {
    const { data, error } = await rootGetters['api/getFromDatabase'](
      'profiles',
      [
        'collectivite_id',
        'departement',
        'departements',
        'email',
        'firstname',
        'is_admin',
        'lastname',
        'poste',
        'region',
        'side',
      ],
      [['eq', 'user_id', id]],
    )

    if (error) {
      throw error
    }

    commit('setUser', {
      accessToken,
      admin: !!data.is_admin,
      departmentCode: data.departement || null,
      departmentCodes: data.departement
        ? data.departements
          ? data.departements.includes(data.departement)
            ? orderBy(data.departements)
            : orderBy([data.departement, ...data.departements])
          : [data.departement]
        : orderBy(data.departements || []),
      email: (data.email || '').toLowerCase(),
      firstname: data.firstname || '',
      id,
      lastname: data.lastname || '',
      regionCode: data.region || null,
      scope: _fromApiUserScope(data),
      territorialAuthorityCode: data.collectivite_id || null,
    })

    return true
  },
}

function _fromApiUserScope(apiUser) {
  if (apiUser.side === 'collectivite') {
    return UserScope.TerritorialAuthority
  }
  if (apiUser.side === 'ppa') {
    return UserScope.Region
  }
  switch (apiUser.poste) {
    case 'ddt':
      return UserScope.State
    case 'dreal':
      return UserScope.Region
    default:
      return UserScope.TerritorialAuthority
  }
}
