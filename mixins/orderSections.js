import { groupBy } from 'lodash'
import sectionsOrder from '@/assets/data/defaultSectionsOrder.json'

export default {
  methods: {
    orderSections (sections, supSections) {
      supSections.push(...sectionsOrder)

      const groupedSupSections = groupBy(supSections, s => s.path)
      supSections = Object.keys(groupedSupSections).map((path) => {
        return groupedSupSections[path].find(s => s.ref.includes('projet')) ||
          groupedSupSections[path].find(s => s.ref.includes('dept')) ||
          groupedSupSections[path].find(s => s.ref.includes('region')) ||
          groupedSupSections[path].find(s => s.ref.includes('main')) ||
          groupedSupSections[path].find(s => s.ref.includes('test'))
      })

      sections.forEach((section) => {
        const { order } = supSections.find(s => s.path === section.path) || { order: 0 }

        Object.assign(section, { order })

        if (section.children) {
          this.orderSections(section.children, supSections)
        }
      })

      sections.sort((s1, s2) => {
        return s1.order - s2.order
      })
    }
  }
}
