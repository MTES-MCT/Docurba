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
    unifyPacs (PACs, paths) {
      paths = paths || uniq(flatten(PACs).map(s => s.path))

      return paths.map((path) => {
        const sections = this.getSectionsFromPACs(PACs, path).map((section) => {
          return omitBy(section, isNil)
        }).reverse()

        const textEdited = sections.reduce((nbEdit, section) => {
          return nbEdit + !!section.text
        }, 0)

        return Object.assign({ textEdited: textEdited > 1 }, ...sections)
      })
    },
    spliceSection (PAC, section) {
      const sectionIndex = PAC.findIndex(s => s.path === section.path)
      if (sectionIndex >= 0) {
        const cleanSection = omitBy(section, isNil)
        const textEdited = !!cleanSection.text
        PAC.splice(sectionIndex, 1, Object.assign({ textEdited }, PAC[sectionIndex], cleanSection))
      }
    }
  }
}
