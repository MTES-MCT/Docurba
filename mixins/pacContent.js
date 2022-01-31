function getDepth (path) {
  // console.log(path)
  return (path.replace(/\/intro$/, '').match(/\//g) || []).length
}

// @vue/component
export default {
  props: {
    pacData: {
      type: Array,
      required: true
    }
  },
  computed: {
    PAC () {
      const parsedPAC = this.pacData.map((section) => {
        const serachText = `${section.titre} ${section.slug}`.toLowerCase()

        const enrichedSection = Object.assign({
          checked: false,
          depth: getDepth(section.path),
          searchValue: serachText.normalize('NFD').replace(/\p{Diacritic}/gu, ''),
          children: []
        }, section)

        return enrichedSection
      })

      parsedPAC.forEach((section) => {
        const parent = parsedPAC.find((p) => {
          const pDepth = p.depth || getDepth(p.path)

          return p !== section &&
          section.dir.includes(p.path.replace(/\/intro$/, '')) &&
            pDepth + 1 === section.depth
        })

        if (parent && !parent.children.includes(section)) {
          parent.children.push(section)
        }
      })

      return parsedPAC
    }
  }
}
