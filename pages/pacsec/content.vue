<template>
  <v-container v-if="loaded" fluid>
    <PACTreeviewContent :pac-data="PAC" />
  </v-container>
  <VGlobalLoader v-else />
</template>

<script>
import regions from '@/assets/data/Regions.json'

import unifiedPAc from '@/mixins/unifiedPac.js'

export default {
  mixins: [unifiedPAc],
  async asyncData ({ $content, route }) {
    let PAC = await $content('PAC', {
      deep: true
    }).fetch()

    // remove unwanted intros
    PAC.splice(PAC.findIndex(s => s.path === '/PAC/Introduction/introcution-PAC-valide'), 1)
    // Filter sections in socle
    PAC = PAC.filter((s) => {
      // No PP
      return !s.path.includes('PP-du-territoire')
    })
    // Filter PLUi/PLU depending on doc type.
    const docType = route.query.document
    PAC = PAC.filter((s) => {
      if (docType === 'PLU') {
        // In PLU remove PLUi sections
        return !s.titre.includes('PLUi')
      } else if (docType.includes('PLUi')) {
        // In PLUi remove PLU sections.
        return !s.titre.includes(' PLU ')
      } else {
        // In CC remove all PLU/PLUi sections
        return !s.titre.includes('PLU')
      }
    })

    PAC = PAC.filter((s) => {
      return !s.dir.includes('/PAC/Annexes')
    })

    return {
      // PAC: PAC.filter(s => !s.path.includes('olitiques-publiques-specifiques'))
      PAC
    }
  },
  data () {
    const region = regions.find(r => r.iso === this.$route.query.region)

    return {
      region,
      loaded: false
    }
  },
  async mounted () {
    let regionSections = await this.fetchSections('pac_sections_region', {
      region: this.region.code
    })

    regionSections = regionSections.filter(s => !s.dir.includes('/PAC/Annexes'))

    this.PAC = this.unifyPacs([regionSections, this.PAC])

    // TODO: This is duplicated in all read sections
    this.PAC.forEach((section) => {
      // Parse the body only if text was edited.
      if (section.text) { section.body = this.$mdParse(section.text) }
    })

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
  }
}
</script>
