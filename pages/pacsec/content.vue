<template>
  <v-container v-if="loaded">
    <PACTreeviewContent :pac-data="PAC" :git-ref="gitRef" />
  </v-container>
  <VGlobalLoader v-else />
</template>

<script>
import axios from 'axios'
import regions from '@/assets/data/Regions.json'

export default {
  data () {
    const region = regions.find(r => r.iso === this.$route.query.region)

    return {
      region,
      gitRef: region ? `region-${region.code}` : 'main',
      PAC: [],
      loaded: false
    }
  },
  async mounted () {
    const { data: sections } = await axios({
      method: 'get',
      url: `/api/trames/tree/${this.gitRef}?content=true`
    })

    this.PAC = this.filterSections(sections)

    this.loaded = true

    // Start Analytics
    const inseeQuery = this.$route.query.insee
    const codes = typeof (inseeQuery) === 'object' ? inseeQuery : [inseeQuery]

    if (codes) {
      codes.forEach((code) => {
        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Content',
          `${this.$route.query.document} - ${code}`
        ])
      })
    }
    // End Analytics
  },
  methods: {
    filterSections (sections) {
      const docType = this.$route.query.document

      sections = sections.filter((section) => {
        const isAllowed = (!section.path.includes('PAC/Introduction/PAC valid') &&
          !section.path.includes('PP-du-territoire') &&
          !section.path.includes('PAC/Annexes'))

        if (docType === 'PLU') {
          return isAllowed && !section.name.includes('PLUi')
        } else if (docType.includes('PLUi')) {
          return isAllowed && !section.name.includes(' PLU ')
        } else {
          return isAllowed && !section.name.includes('PLU')
        }
      })

      sections.forEach((section) => {
        if (section.content) {
          section.body = this.$md.compile(section.content)
        } else {
          section.content = null
          section.body = null
        }

        if (section.children) {
          section.children = this.filterSections(section.children)
        }
      })

      return sections
    }
  }
}
</script>
