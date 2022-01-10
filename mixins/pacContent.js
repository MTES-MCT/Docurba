function getDepth (path) {
  return (path.match(/\//g) || []).length
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

      const parent = PAC.find((p) => {
        const pDepth = p.depth || getDepth(p.path)

        return p !== section &&
          p.slug === 'intro' &&
          section.dir.includes(p.dir) &&
          (section.slug === 'intro' ? pDepth + 1 : pDepth) === section.depth
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

      return section
    })

    PAC.forEach((section) => {
      if (section.children) {
        // Temporary filter
        if (this.minFilter) {
          section.children = section.children.filter((c) => {
            return (c.children && c.children.length) ||
            (c.body && c.body.children && c.body.children.length > 1)
          })
        }

        section.children.sort((sa, sb) => {
          return sa.ordre - sb.ordre
        })
      }
    })

    return {
      PAC
    }
  }
}
