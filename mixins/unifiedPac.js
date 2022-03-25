import { uniq, flatten, omitBy, isNil } from 'lodash'

// @vue/component
export default {
  methods: {
    getSectionsFromPACs (PACs, path) {
      const sections = []

      PACs.forEach((PAC) => {
        const section = PAC.find(s => s.path === path)
        sections.push(section || {})
      })

      return sections
    },
    // PACs should be in order. PACs[0] will override data in PACs[1]
    unifyPacs (PACs) {
      const paths = uniq(flatten(PACs).map(s => s.path))

      return paths.map((path) => {
        return Object.assign({}, ...this.getSectionsFromPACs(PACs, path).map((section) => {
          return omitBy(section, isNil)
        }).reverse())
      })
    }
  }
}
