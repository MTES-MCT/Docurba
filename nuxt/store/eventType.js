import { keyBy } from 'lodash'

// interface EventType {
//   id: string
//   name: string
// }

export const state = () => ({
  typeById: {},
})

export const getters = {}

export const mutations = {
  setTypes(state, types) {
    state.typeById = {
      ...state.typeById,
      ...keyBy(types, 'id'),
    }
  },
}

export const actions = {
  async get({ dispatch }, { id, ...params }) {
    const list = await dispatch('list', {
      ...params,
      ids: [id],
    })

    return list.length ? list[0] : null
  },
  async list({ commit, rootGetters, state }, params = {}) {
    const apiParams = _toApiEventTypeParams(params)

    if (params.ids) {
      if (params.ids.every((id) => id in state.typeById)) {
        return params.ids.map((id) => state.typeById[id])
      }

      apiParams.ids = apiParams.ids.filter((id) => !(id in state.typeById[id]))
    }

    const types = _fromApiEventTypes(
      await rootGetters['api/get']('/api-internes/types-evenement/', apiParams),
      params,
    )
    commit('setTypes', types)

    return params.ids
      ? params.ids.map((id) => state.typeById[id])
      : types
  },
}

function _fromApiEventType(apiType, params) {
  return apiType
}

function _fromApiEventTypes(apiTypes, params) {
  return apiTypes.map((apiType) => _fromApiEventType(apiType, params))
}

function _toApiEventTypeParams(params) {
  return params
}
