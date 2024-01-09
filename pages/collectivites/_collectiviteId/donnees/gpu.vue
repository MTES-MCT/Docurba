<template>
  <v-container v-if="loading">
    <v-row>
      <v-col v-for="i in 3" :key="i">
        <v-skeleton-loader type="image" />
      </v-col>
    </v-row>
  </v-container>

  <v-container v-else>
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
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    isEpci: {
      type: Boolean,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      loading: true,
      areas: [],
      selectedArea: null,
      documents: []
    }
  },
  computed: {
    filteredDocuments () {
      if (!this.selectedArea) {
        return this.documents
      }
      return this.documents.filter(doc => doc.grid.name === this.selectedArea)
    },
    availableAreas () {
      return this.areas.filter(a => !!this.documents.find(doc => doc.grid.name === a.code))
    }
  },
  async created () {
    this.areas = [
      { code: this.collectivite.code, intitule: this.collectivite.intitule },
      ...(this.collectivite.membres
        ?.filter(commune => commune.type.startsWith('COM'))
        .map(({ code, intitule }) => { return { code, intitule } }) ?? []),
      { code: this.collectivite.departement.code, intitule: this.collectivite.departement.intitule },
      { code: 'R' + this.collectivite.region.code, intitule: this.collectivite.region.intitule },
      { code: 'FR', intitule: 'France' }
    ]

    const { data: supCategories } = await axios.get(
      'https://www.geoportail-urbanisme.gouv.fr/api/sup-categories'
    )

    const responses = await Promise.all(
      this.areas.map((area) => {
        return axios
          .get('https://www.geoportail-urbanisme.gouv.fr/api/document', {
            params: {
              status: 'document.production',
              grid: area.code
            }
          })
          .then(r => r.data)
      })
    )

    const centerRes = await axios.get(`/api/geo/collectivites/${this.collectivite.code}/center`)

    const [x, y] = centerRes.data.coordinates

    this.documents = responses.flat().map((doc) => {
      if (doc.type === 'SUP') {
        const categoryCode = doc.name.split('_').at(-1)
        doc.supCategory = supCategories.find(
          cat => cat.name === categoryCode
        )
      }

      doc.center = {
        lat: y,
        lon: x
      }

      return doc
    })

    this.loading = false
  }
}
</script>
