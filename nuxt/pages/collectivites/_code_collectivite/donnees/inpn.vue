<template>
  <div>
    <v-container class="px-0">
      <v-row>
        <v-col cols="12">
          <h3>INPN pour {{ isEpci ? 'l\'Epci' : 'la commune' }} </h3>
        </v-col>
        <v-col cols="12">
          <p>
            Vous trouvez toutes les informations relatives à l'Inventaire National du Patrimoine Naturel surle site inpn.mnhn.fr.
          </p>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <DataINPNTable :communes="communes" />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  name: 'Inpn',
  props: {
    isEpci: {
      type: Boolean,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    },
    communes: {
      type: Array,
      required: true
    }
  },
  mounted () {
    // Start Analytics
    const inseeQuery = this.$route.query.insee
    const codes = typeof inseeQuery === 'object' ? inseeQuery : [inseeQuery]

    if (codes) {
      codes.forEach((code) => {
        this.$matomo([
          'trackEvent',
          'Socle de PAC',
          'INPN',
          this.$route.params.collectiviteId
        ])
      })
    }
    // End Analytics
  }
}
</script>
