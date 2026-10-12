<template>
  <div>
    <v-row>
      <v-col cols="12">
        <h1>Risques Géographiques pour {{ territorialAuthority.intermunicipalityCode ? 'la commune' : 'l\'Epci' }}</h1>
      </v-col>
      <v-col cols="12">
        <p>
          Vous trouvez toutes les informations relatives aux risques sur le site georisques.gouv.fr.
          Vous pouvez également télécharger directement la donnée du Plan Prévention des Risques directement depuis Docurba.
        </p>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <DataGeorisquesTable
          :communes="communes"
          :is-epci="!territorialAuthority.intermunicipalityCode"
        />
      </v-col>
    </v-row>
  </div>
</template>

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
      codes.forEach((code) => {
        this.$matomo([
          'trackEvent',
          'Socle de PAC',
          'Georisques',
          `${this.$route.query.document} - ${code}`
        ])
      })
    }
  }
}
</script>
