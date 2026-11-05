export const state = () => ({
  endDate: '2027-01-01T00:00:00.000Z',
  year: 2026,
})

export const getters = {
  active(state) {
    return new Date().toJSON() <= state.endDate
  },
  endDate(state) {
    return state.endDate
  },
  year(state) {
    return state.year
  },
}

export const mutations = {}

export const actions = {}
