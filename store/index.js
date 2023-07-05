export const state = () => ({
  routeQueries: {}
})

export const getters = {
  routeIsEpci (state) {
    return state.routeQueries.isEpci === true || (state.routeQueries.isEpci === 'true')
  }
}

export const mutations = {
  routeQueries (state, value) {
    state.routeQueries = Object.assign(state.routeQueries, value)
  }
}
