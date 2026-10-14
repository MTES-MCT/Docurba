<script>
import axios from 'axios'

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
  data () {
    return {
      areas: [],
      documents: [],
      loading: true,
      selectedArea: null
    }
  },
  computed: {
    availableAreas () {
      return this.areas.filter(a => !!this.documents.find(doc => doc.grid.name === a.code))
    },
    filteredDocuments () {
      if (!this.selectedArea) {
        return this.documents
      }
      return this.documents.filter(doc => doc.grid.name === this.selectedArea)
    }
  },
  async created () {
    const department = await this.$departmentApi.get(this.territorialAuthority.departmentCode)

    this.areas = [
      { code: this.territorialAuthority.code, intitule: this.territorialAuthority.name },
      ...this.towns.map(town => ({ code: town.code, intitule: town.name })),
      { code: department.code, intitule: department.name },
      { code: `R${department.regionCode}`, intitule: department.regionName },
      { code: 'FR', intitule: 'France' }
    ]

    const { data: supCategories } = await axios.get(
      'https://www.geoportail-urbanisme.gouv.fr/api/standard/sup-categories'
    )
    const responses = (await Promise.all(
      this.areas.map(area =>
        axios.get('https://www.geoportail-urbanisme.gouv.fr/api/document', {
          params: {
            status: 'document.production',
            grid: area.code
          }
        })
      )
    )).flatMap(({ data }) => data)
    const centerRes = await axios.get(`/api/geo/collectivites/${this.territorialAuthority.code}/center`)
    const [x, y] = centerRes.data.coordinates

    this.documents = responses.map((res) => {
      const doc = {
        ...res,
        center: {
          lat: y,
          lon: x
        }
      }

      if (doc.type === 'SUP') {
        const categoryCode = doc.name.split('_').at(-1)
        doc.supCategory = supCategories.find(cat =>
          cat.name === categoryCode
        )
      }

      return doc
    })

    this.loading = false
  },
  mounted () {
    this.$matomo([
      'trackEvent',
      'Socle de PAC',
      'GPU',
      this.territorialAuthority.code
    ])
  }
}
</script>

<template>
  <v-row v-if="loading">
    <v-col v-for="i in 3" :key="i">
      <v-skeleton-loader type="image" />
    </v-col>
  </v-row>
  <div v-else>
    <v-row>
      <v-col cols="12">
        <v-alert type="info">
          Ceci est une première version de la mise à disposition des données proposées par le GPU, n'hésitez pas à nous faire des retours pour l'améliorer : <a href="mailto:equipe@docurba.beta.gouv.fr">equipe@docurba.beta.gouv.fr</a>
        </v-alert>
      </v-col>
      <v-col cols="12">
        <v-chip-group
          v-model="selectedArea"
          column
        >
          <v-chip
            v-for="area in availableAreas"
            :key="area.code"
            :value="area.code"
            filter
            outlined
            color="bf500"
          >
            {{ area.intitule }}
          </v-chip>
        </v-chip-group>
      </v-col>
    </v-row>
    <v-row>
      <v-col v-for="doc in filteredDocuments" :key="doc.id" :cols="4">
        <DataGpuDocumentCard :document="doc" />
      </v-col>
    </v-row>
  </div>
</template>
