<template>
  <v-autocomplete
    v-model="selectedDepartement"
    :items="departements"
    label="Departement"
    filled
    :error-messages="errorMessages"
    return-object
    :clearable="clearable"
  />
</template>

<script>
import departements from '@/assets/data/departements-france.json'
import { FiltersDeleteResponseAllOfData } from 'pipedrive';

export default {
  props: {
    value: {
      type: Object,
      default () { return {} }
    },
    errorMessages: {
      type: Array,
      default: () => []
    },
    clearable: {
      type: Boolean,
      default: false
    },
    defaultDepartementCode: {
      type: Number,
      default: null
    },
    filterDepartements: {
      type: Array,
      default: () => []
    }
  },
  data () {
    let filteredDepartements = departements
    if (this.filterDepartements.length > 0) {
      filteredDepartements = filteredDepartements.filter(departement => this.filterDepartements.map(dept => parseInt(dept)).includes(departement.code_departement) )
    }
    const enrichedDepartements = filteredDepartements.map(d => Object.assign({
      text: `${d.nom_departement} - ${d.code_departement}`
    }, d))

    return {
      departements: enrichedDepartements
    }
  },
  computed: {
    selectedDepartement: {
      get () {
        return this.departements.find((d) => {
        // eslint-disable-next-line eqeqeq
          return d.code_departement == this.defaultDepartementCode
        })
      },
      set (dept) {
        console.log('set emited', dept)
        this.$emit('input', dept)
      }
    }
  }
}
</script>
