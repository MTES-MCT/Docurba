<template>
  <v-container>
    <GlossaireWordsList />
  </v-container>
</template>

<script>
export default {
  mounted () {
    // Start Analytics
    const inseeQuery = this.$route.query.insee
    const codes = typeof (inseeQuery) === 'object' ? inseeQuery : [inseeQuery]

    if (codes) {
      codes.forEach((code) => {
        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Glossaire',
          `${this.$route.query.document} - ${code}`
        ])
      })
    }
    // End Analytics
  }
}
</script>
