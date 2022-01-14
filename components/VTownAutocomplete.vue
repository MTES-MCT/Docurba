<template>
  <v-row>
    <v-col v-show="!hideDept" cols="12" :sm="colsDep">
      <v-autocomplete
        v-model="selectedDepartement"
        :items="departements"
        label="Departement"
        hide-details
        filled
        return-object
      />
    </v-col>
    <v-col cols="12" :sm="colsTown">
      <v-autocomplete
        no-data-text="Selectionnez un département"
        :items="towns"
        item-text="nom_commune"
        return-object
        hide-details
        filled
        label="Commune"
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
      departements: enrichedDepartements,
      towns: []
    }
  },
  watch: {
    selectedDepartement () {
      this.fetchTowns()
    }
  },
  mounted () {
    console.log('fetch towns', this.selectedDepartement)
    this.fetchTowns()
  },
  methods: {
    input (town) {
      this.$emit('input', town)
    },
    async fetchTowns () {
      if (this.selectedDepartement) {
        this.towns = (await axios({
          url: `/api/communes/${this.selectedDepartement.code_departement}`,
          method: 'get',
          data: this.selectedDepartement
        })).data
      }
    }
  }
}
</script>
