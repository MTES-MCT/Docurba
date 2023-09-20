<template>
  <v-row>
    <v-col cols="12" md="4">
      <StatsTextCard text="Somme des types de documents opposables par communes." />
    </v-col>
    <v-col cols="12" lg="8">
      <StatsBarsCard title="Type de documents par communes" :points="docTypes" />
    </v-col>
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
      docTypes: []
    }
  },
  watch: {
    params: {
      deep: true,
      handler () {
        this.getAllCounts()
      }
    }
  },
  mounted () {
    this.getAllCounts()
  },
  methods: {
    async getNbDoc (docType) {
      const { data: { count } } = await axios({
        url: '/api/urba/documents/count',
        params: Object.assign({ type_du_opposable: docType }, this.params)
      })

      return { docType, count }
    },
    async getAllCounts () {
      const docTypes = ['PLU', 'CC', 'RNU']

      const nbDocTypes = await Promise.all(docTypes.map((docType) => {
        return this.getNbDoc(docType)
      }))

      this.docTypes = nbDocTypes.map((nbDocType) => {
        return {
          x: nbDocType.docType,
          xLabel: nbDocType.docType,
          y: nbDocType.count,
          yLabel: nbDocType.count
        }
      })
    }
  }
}
</script>
