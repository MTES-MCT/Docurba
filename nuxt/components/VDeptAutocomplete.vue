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
    departementsFilter: {
      type: Array,
      default: () => []
    }
  },
  data () {
    let filteredDepartements = departements

    if (this.departementsFilter.length > 0) {
      const departementsAsInt = new Set(this.departementsFilter.map(dept => Number.parseInt(dept)))
      filteredDepartements = filteredDepartements.filter(departement => departementsAsInt.has(departement.code_departement))
    }
    const enrichedDepartements = filteredDepartements.map(dept => ({ ...dept, text: `${dept.nom_departement} - ${dept.code_departement}` }))

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
        this.$emit('input', dept)
      }
    }
  }
}
</script>
