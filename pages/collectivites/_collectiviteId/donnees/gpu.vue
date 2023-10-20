<template>
  <div class="py-4">
    <v-container v-if="loading">
      <v-row>
        <v-col v-for="i in 3" :key="i">
          <v-skeleton-loader type="image" />
        </v-col>
      </v-row>
    </v-container>

    <template v-else>
      <v-container>
        <v-chip-group
          v-model="selectedArea"
          column
        >
          <v-chip
            v-for="area in areas"
            :key="area.code"
            :value="area.code"
            filter
            outlined
            color="bf500"
          >
            {{ area.intitule }}
          </v-chip>
        </v-chip-group>
      </v-container>
      <v-container class="mt-2">
        <v-row>
          <v-col v-for="doc in filteredDocuments" :key="doc.id" :cols="4">
            <DataGpuDocumentCard :document="doc" />
          </v-col>
        </v-row>
      </v-container>
    </template>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    collectivite: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      loading: true,
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
    }
  },
  async created () {
    this.areas = [
      { code: this.collectivite.code, intitule: this.collectivite.intitule },
      // ...(this.collectivite.communes
      //   ?.filter(commune => commune.type === 'Commune')
      //   .map(({ code, intitule }) => { return { code, intitule } }) ?? []),
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

    this.documents = responses.flat().map((doc) => {
      if (doc.type === 'SUP') {
        const categoryCode = doc.name.split('_').at(-1)
        doc.supCategory = supCategories.find(
          cat => cat.name === categoryCode
        )
      }

      return doc
    })

    this.loading = false
  }
}
</script>
