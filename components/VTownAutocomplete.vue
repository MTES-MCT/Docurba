<template>
  <v-row>
    <v-col cols="12">
      <v-autocomplete
        v-model="selectedDepartement"
        :items="departements"
        label="Departement"
        hide-details
        filled
        return-object
      />
    </v-col>
    <v-col>
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
    }
  },
  data () {
    const enrichedDepartements = departements.map(d => Object.assign({
      text: `${d.nom_departement} - ${d.code_departement}`
    }, d))

    return {
      selectedDepartement: null,
      departements: enrichedDepartements,
      towns: []
    }
  },
  watch: {
    async selectedDepartement () {
      if (this.selectedDepartement) {
        this.towns = (await axios({
          url: `/api/communes/${this.selectedDepartement.code_departement}`,
          method: 'get',
          data: this.selectedDepartement
        })).data
      }
    }
  },
  methods: {
    input (town) {
      this.$emit('input', town)
    }
  }
}
</script>
