import rawDepartments from '~/assets/data/departements-france.json'

// interface Department {
//   code: string
//   name: string
//   regionCode: string
// }

export const state = () => ({
  departments: [],
  initialized: false,
})

export const getters = {}

export const mutations = {
  setDepartments(state, departments) {
    state.departments = departments
  },
  setInitialized(state, initialized) {
    state.initialized = initialized
  },
}

export const actions = {
  async get({ dispatch, state }, code) {
    if (!state.initialized) {
      await dispatch('init')
    }

    return state.departments.find((department) => department.code === code)
  },
  async init({ commit, state }) {
    if (state.initialized) {
      return false
    }

    return new Promise((resolve) => {
      commit('setDepartments', rawDepartments.map((rawDepartment) => ({
        code: rawDepartment.code_departement.toString().padStart(2, '0'),
        name: rawDepartment.nom_departement,
        regionCode: rawDepartment.code_region.toString(),
      })))
      commit('setInitialized', true)
      resolve(true)
    })
  },
  async list({ dispatch, state }) {
    if (!state.initialized) {
      await dispatch('init')
    }

    return state.departments
  },
}
