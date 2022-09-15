<template>
  <v-container>
    <GlossaireWordsList />
  </v-container>
</template>

<script>
export default {
  mounted () {
    if (this.$route.query.insee) {
      this.$route.query.insee.forEach((code) => {
        this.$matomo.trackEvent('Socle de PAC', 'Glossaire', `${this.$route.query.document} - ${code}`)
      })
    }
  }
}
</script>
