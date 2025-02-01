<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1>Risques Géographiques pour {{ isEpci ? 'l\'Epci' : 'la commune' }} </h1>
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
          <DataGeorisquesTable :is-epci="isEpci" :communes="communes" />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  name: 'Georisques',
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
