function getDepth (path) {
  return (path.replace(/\/intro$/, '').match(/\//g) || []).length
}

// @vue/component
export default {
  props: {
    pacData: {
      type: Array,
      required: true
    },
    minFilter: {
      type: Boolean,
      default: true
    }
  },
  data () {
    const PAC = this.pacData.map((section) => {
      const serachText = `${section.titre} ${section.slug}`.toLowerCase()

      return Object.assign({
        checked: false,
        searchValue: serachText.normalize('NFD').replace(/\p{Diacritic}/gu, '')
      }, section)
    })

    PAC.forEach((section) => {
      section.depth = getDepth(section.path)
      this.assignParent(section, PAC)
    })

    PAC.forEach((section) => {
      if (section.children) {
        // Temporary filters, or maybe not ?
        if (this.minFilter) {
          section.children = section.children.filter((c) => {
            return (c.children && c.children.length) ||
            (c.body && c.body.children && c.body.children.length > 1)
          })
        }

        section.children.sort((sa, sb) => {
          return (sa.ordre || 100) - (sb.ordre || 100)
        })
      } else { section.children = [] }
    })

    return {
      PAC
    }
  },
  watch: {
    pacData () {
      this.pacData.filter((s) => {
        return !this.PAC.find(_s => _s.path === s.path)
      }).forEach((section) => {
        const serachText = `${section.titre} ${section.slug}`.toLowerCase()

        const newSection = Object.assign({
          checked: false,
          searchValue: serachText.normalize('NFD').replace(/\p{Diacritic}/gu, '')
        }, section)

        newSection.depth = getDepth(newSection.path)
        this.assignParent(newSection)

        if (!newSection.children) {
          newSection.children = []
        }

        this.PAC.push(newSection)
      })
    }
  },
  methods: {
    assignParent (section, PAC = this.PAC) {
      const parent = PAC.find((p) => {
        const pDepth = p.depth || getDepth(p.path)

        return p !== section &&
        section.dir.includes(p.path.replace(/\/intro$/, '')) &&
          pDepth + 1 === section.depth
      })

      if (parent) {
        section.parent = parent

        if (parent.children) {
          if (!parent.children.includes(section)) {
            parent.children.push(section)
          }
        } else {
          parent.children = [section]
        }
      }
    }
  }
}
