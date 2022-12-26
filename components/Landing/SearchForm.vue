<template>
  <v-form ref="form" v-model="valid">
    <v-row justify="center" align="center">
      <v-col cols="2">
        <v-select
          v-model="searchQuery.document"
          filled
          hide-details
          dense
          placeholder="Type de document"
          :items="documents"
          :rules="[$rules.required]"
          required
        />
      </v-col>
      <v-col v-if="searchQuery.document && searchQuery.document.includes('i')" cols="">
        <VEpciAutocomplete
          v-model="selectedEpci"
          :input-props="{
            rules: [$rules.required]
          }"
        />
      </v-col>
      <v-col v-else cols="">
        <VTownAutocomplete
          v-model="selectedTown"
          :cols-dep="4"
          :cols-town="8"
          :input-props="{
            rules: [$rules.required]
          }"
        />
      </v-col>
      <v-col cols="auto">
        <v-btn
          depressed
          color="primary"
          :loading="searchLoading"
          @click="searchCTA"
        >
          <v-icon class="mr-2" small>
            {{ icons.mdiMagnify }}
          </v-icon>
          Rechercher
        </v-btn>
      </v-col>
    </v-row>
  </v-form>
</template>

<script>
import axios from 'axios'
import { mdiMagnify } from '@mdi/js'
import regions from '@/assets/data/Regions.json'

export default {
  props: {
    path: {
      type: String,
      default: '/pacsec/content'
    }
  },
  data () {
    return {
      documents: ['CC', 'PLU', 'PLUi', 'PLUi-H', 'PLUi-D', 'PLUi-HD', 'Prescriptions'], // 'SCoT', 'SCot-AEC'],
      searchQuery: {
        region: null,
        document: null
      },
      valid: false,
      selectedEpci: null,
      selectedTown: null,
      searchLoading: false,
      icons: {
        mdiMagnify
      }
    }
  },
  computed: {
    searchLink () {
      const query = {
        insee: [this.selectedTown ? this.selectedTown.code_commune_INSEE : '']
      }

      if (this.searchQuery.region) {
        query.region = this.searchQuery.region.iso
      }

      if (this.searchQuery.document) {
        query.document = this.searchQuery.document
      }

      return {
        path: this.path,
        query
      }
    }
  },
  watch: {
    selectedTown () {
      this.searchQuery.region = regions.find(r => r.name === this.selectedTown.nom_region)
    }
  },
  methods: {
    async searchCTA () {
      if (!this.valid) {
        this.$refs.form.validate()
        return false
      }

      if (this.searchQuery.document && this.searchQuery.document.includes('i')) {
        this.searchLoading = true

        const EPCI = (await axios({
          method: 'get',
          url: `/api/epci/${this.selectedEpci.id}`
        })).data

        const regionCode = EPCI.towns[0].code_region
        // eslint-disable-next-line eqeqeq
        const region = regions.find(r => r.code == regionCode)

        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Recherche',
          `${region.iso} - ${this.selectedEpci.label}`
        ])

        this.$router.push({
          path: '/pacsec/content',
          query: Object.assign({}, this.searchLink.query, {
            insee: EPCI.towns.map(t => t.code_commune_INSEE),
            region: region.iso
          })
        })

        this.searchLoading = false
      } else {
        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Recherche',
          `${this.selectedTown.code_departement} - ${this.selectedTown.nom_commune}`
        ])

        this.$router.push(this.searchLink)
      }
    }
  }
}
</script>
