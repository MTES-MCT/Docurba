<template>
  <v-row>
    <v-col v-show="!hideDept" cols="12" :sm="colsDep">
      <v-autocomplete
        v-model="selectedDepartement"
        :items="departements"
        placeholder="Departement"
        hide-details
        filled
        return-object
        dense
        @change="fetchTowns"
      />
    </v-col>
    <v-col cols="12" :sm="colsTown">
      <v-autocomplete
        :value="selectedTown"
        :no-data-text="loading ? 'Chargement ...' : 'Selectionnez un département'"
        :items="towns"
        item-text="nom_commune"
        return-object
        hide-details
        filled
        placeholder="Commune"
        :loading="loading"
        dense
        @change="input"
      />
    </v-col>
  </v-row>
</template>

<script>
import axios from 'axios'
import departements from '@/assets/data/departements-france.json'

export default {
  props: {
    value: {
      type: Object,
      default () {
        return {}
      }
    },
    colsDep: {
      type: Number,
      default: 12
    },
    colsTown: {
      type: Number,
      default: 12
    },
    defaultDepartementCode: {
      type: [Number, String],
      default: null
    },
    hideDept: {
      type: Boolean,
      default: false
    }
  },
  data () {
    const enrichedDepartements = departements.map(d => Object.assign({
      text: `${d.nom_departement} - ${d.code_departement}`
    }, d))

    let defaultDepartement = null

    if (this.defaultDepartementCode) {
      defaultDepartement = enrichedDepartements.find((d) => {
        // eslint-disable-next-line eqeqeq
        return d.code_departement == this.defaultDepartementCode
      })
    }

    return {
      selectedDepartement: defaultDepartement,
      selectedTown: Object.assign({}, this.value),
      departements: enrichedDepartements,
      towns: (this.value && this.value.code_commune) ? [Object.assign({}, this.value)] : [],
      loading: false
    }
  },
  watch: {
    // selectedDepartement () {
    //   this.fetchTowns()
    // }
  },
  mounted () {
    this.fetchTowns()
  },
  methods: {
    input (town) {
      this.$emit('input', town)
    },
    async fetchTowns () {
      if (this.selectedDepartement) {
        this.loading = true
        this.towns = (await axios({
          // url: `/api/communes/${this.selectedDepartement.code_departement}`,
          url: '/api/communes',
          method: 'get',
          params: { departements: this.selectedDepartement.code_departement }
          // data: this.selectedDepartement
        })).data
        console.log('towns: ', this.towns)
        this.loading = false
      }
    }
  }
}
</script>
