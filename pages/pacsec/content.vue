<template>
  <v-container fluid>
    <PACTreeviewContent :pac-data="PAC" />
  </v-container>
</template>

<script>

export default {
  async asyncData ({ $content, route }) {
    let PAC = await $content('PAC', {
      deep: true
    }).fetch()

    // remove unwanted intros
    PAC.splice(PAC.findIndex(s => s.path === '/PAC/Introduction/introcution-PAC-valide'), 1)
    // Filter PP du territoire in socle
    PAC = PAC.filter(s => !s.path.includes('PP-du-territoire'))
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

    return {
      // PAC: PAC.filter(s => !s.path.includes('olitiques-publiques-specifiques'))
      PAC
    }
  },
  mounted () {
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
