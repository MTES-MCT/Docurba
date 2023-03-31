<template>
  <v-form ref="form" v-model="valid">
    <v-row justify="center" align="center">
      <v-col v-if="showEpciSelect" cols="">
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
          @click="toPublicDashboard"
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
      documents: ['CC', 'PLU', 'PLUi', 'PLUi-H', 'PLUi-D', 'PLUi-HD'], // 'Prescriptions', 'SCoT', 'SCot-AEC'],
      searchQuery: {
        region: null,
        document: null
      },
      valid: false,
      typePrescription: '',
      selectedEpci: null,
      selectedTown: null,
      searchLoading: false,
      icons: {
        mdiMagnify
      }
    }
  },
  computed: {
    showEpciSelect () {
      const acceptEpci = ['PLUi', 'PLUi-H', 'PLUi-D', 'PLUi-HD']
      const isEpciGlobal = this.searchQuery.document && acceptEpci.includes(this.searchQuery.document)

      return isEpciGlobal || (this.searchQuery.document === 'Prescriptions' && this.typePrescription === 'EPCI')
    },
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
        path: this.searchQuery.document === 'Prescriptions' ? '/prescriptions' : this.path,
        query
      }
    }
  },
  watch: {
    'searchQuery.document' (newVal) {
      if (newVal !== 'Prescriptions') { this.typePrescription = '' }
    },
    selectedTown () {
      this.searchQuery.region = regions.find(r => r.name === this.selectedTown.nom_region)
    }
  },
  methods: {
    toPublicDashboard () {
      if (!this.valid) {
        this.$refs.form.validate()
      } else {
        const collectiviteId = this.showEpciSelect ? this.selectedEpci.id : this.selectedTown.code_commune_INSEE
        const departementId = this.showEpciSelect ? '' : this.selectedTown.code_departement

        console.log('selectedTown: ', this.selectedTown, ' this.selectedEpci: ', this.selectedEpci)
        console.log('collectiviteId: ', collectiviteId, 'departementId: ', departementId)
        this.$router.push({
          name: 'collectivites-collectiviteId',
          params: {
            collectiviteId
          },
          query: {
            isEpci: !!this.showEpciSelect
          }
        })
      }
    },
    async searchCTA () {
      if (!this.valid) {
        this.$refs.form.validate()
        return false
      }

      if (this.showEpciSelect) {
        this.searchLoading = true
        const EPCI = (await axios({
          method: 'get',
          url: `/api/epci/${this.selectedEpci.id}`
        })).data
        // console.log('EPCI: ', EPCI)
        const regionCode = EPCI.towns[0].code_region
        // eslint-disable-next-line
        const region = regions.find(r => r.code == regionCode)

        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Recherche',
          `${region.iso} - ${this.selectedEpci.label}`
        ])

        this.$router.push({
          path: this.searchLink.path,
          query: Object.assign({}, this.searchLink.query, {
            insee: EPCI.towns.map(t => t.code_commune_INSEE),
            region: region.iso,
            epci_code: EPCI.EPCI,
            epci_label: EPCI.label
          })
        })

        this.searchLoading = false
      } else {
        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Recherche',
          `${this.selectedTown.code_departement} - ${this.selectedTown.nom_commune}`
        ])

        console.log('this.searchLink: ', this.searchLink)

        this.$router.push(this.searchLink)
      }
    }
  }
}
</script>
