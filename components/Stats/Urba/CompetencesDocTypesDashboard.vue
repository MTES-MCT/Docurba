<template>
  <v-row>
    <!-- Communes -->
    <v-col cols="12" lg="8">
      <StatsBarsCard title="Compétence commune" :points="communesDocTypes" />
    </v-col>
    <v-col cols="12" md="4">
      <StatsTextCard text="Somme des types de documents opposables par communes pour les communes ayant la compétence Urbanisme." />
    </v-col>
    <!-- /Communes -->

    <!-- Interco -->
    <v-col cols="12" md="4">
      <StatsTextCard text="Somme des types de documents opposables par communes pour les communes ayant délégué la compétence Urbanisme à leur EPCI." />
    </v-col>
    <v-col cols="12" lg="8">
      <StatsBarsCard title="Compétence EPCI" :points="intercoDocTypes" />
    </v-col>
    <!-- /Interco -->
  </v-row>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    params: {
      type: Object,
      default () { return {} }
    }
  },
  data () {
    return {
      communesDocTypes: [],
      intercoDocTypes: []
    }
  },
  watch: {
    params: {
      deep: true,
      handler () {
        this.getAllCountsCommunes()
        this.getAllCountsInterco()
      }
    }
  },
  mounted () {
    this.getAllCountsCommunes()
    this.getAllCountsInterco()
  },
  methods: {
    async getNbDoc (params) {
      const { data: { count } } = await axios({
        url: '/api/urba/documents/count',
        params: Object.assign({}, params, this.params)
        // {
        //   type_du_opposable: docType,
        //   interco_competence_plu: competenceInterco
        // }
      })

      return { ...params, count }
    },
    async getAllCountsCommunes () {
      const docTypes = [
        { type_du_opposable: 'PLU', interco_competence_plu: false },
        { type_du_opposable: 'CC', interco_competence_plu: false },
        { type_du_opposable: 'RNU', interco_competence_plu: false }
      ]

      const nbDocTypes = await Promise.all(docTypes.map((docType) => {
        return this.getNbDoc(docType)
      }))

      this.communesDocTypes = nbDocTypes.map((nbDocType) => {
        return {
          x: nbDocType.type_du_opposable,
          xLabel: nbDocType.type_du_opposable,
          y: nbDocType.count,
          yLabel: nbDocType.count
        }
      })
    },
    async getAllCountsInterco () {
      const docTypes = [
        { type_du_opposable: 'PLU', interco_competence_plu: true, is_intercommunal_opposable: false },
        { type_du_opposable: 'PLU', interco_competence_plu: true, is_intercommunal_opposable: true },
        { type_du_opposable: 'CC', interco_competence_plu: true },
        { type_du_opposable: 'RNU', interco_competence_plu: true }
      ]

      const nbDocTypes = await Promise.all(docTypes.map((docType) => {
        return this.getNbDoc(docType)
      }))

      nbDocTypes.forEach((nbDocType) => {
        nbDocType.label = nbDocType.type_du_opposable + (nbDocType.is_intercommunal_opposable ? 'i' : '')
      })

      this.intercoDocTypes = nbDocTypes.map((nbDocType) => {
        return {
          x: nbDocType.label,
          xLabel: nbDocType.label,
          y: nbDocType.count,
          yLabel: nbDocType.count
        }
      })
    }
  }
}
</script>
