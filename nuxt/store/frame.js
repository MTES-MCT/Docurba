export const state = () => ({
  frameByDepartmentCode: {},
})

export const getters = {}

export const mutations = {
  setDepartmentFrame(state, { departmentCode, frame }) {
    state.frameByDepartmentCode = {
      ...state.frameByDepartmentCode,
      [departmentCode]: frame,
    }
  },
}

export const actions = {
  async getForDepartment({ state }, departmentCode) {
    if (departmentCode in state.frameByDepartmentCode) {
      return state.frameByDepartmentCode[departmentCode]
    }

    // TODO :: Implement this
    return []

    // const departmentNumber = Number(departmentCode)
    // const ref = `dept-${
    //   Number.isNaN(departmentNumber)
    //     ? departmentCode
    //     : departmentNumber
    // }`

    // const { data } = await github.request(
    //   `GET /repos/{owner}/{repo}/git/trees/{ref}?recursive=1`,
    //   { ref },
    // )

    // console.log('!!!', data)
  },
}
