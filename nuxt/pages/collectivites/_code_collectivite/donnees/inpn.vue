<script>
export default {
  props: {
    territorialAuthority: {
      required: true,
      type: Object
    },
    towns: {
      required: true,
      type: Array
    }
  },
  computed: {
    communes () {
      return this.towns.map(town => ({
        code: town.code,
        intitule: town.name
      }))
    }
  },
  mounted () {
    const inseeQuery = this.$route.query.insee
    const codes = typeof inseeQuery === 'object' ? inseeQuery : [inseeQuery]

    if (codes) {
      codes.forEach(() => {
        this.$matomo([
          'trackEvent',
          'Socle de PAC',
          'INPN',
          this.$route.params.code_collectivite
        ])
      })
    }
  }
}
</script>

<template>
  <div>
    <v-row>
      <v-col cols="12">
        <h3>INPN pour {{ territorialAuthority.intermunicipalityCode ? 'la commune' : 'l\'Epci' }}</h3>
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
  </div>
</template>
