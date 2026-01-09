<template>
  <v-autocomplete
    v-model="selectedDepartement"
    :items="departements"
    :label="withLabel ? 'Département' : ''"
    :dense="dense"
    filled
    :hide-details="hideDetails"
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
      type: String,
      default: null
    },
    departementsFilter: {
      type: Array,
      default: () => []
    },
    hideDetails: {
      type: Boolean,
      default: false
    },
    dense: {
      type: Boolean,
      default: false
    },
    withLabel: {
      type: Boolean,
      default: true
    }
  },
  data () {
    let filteredDepartements = departements
    if (this.departementsFilter.length > 0) {
      filteredDepartements = departements.filter(departement =>
        this.departementsFilter.includes(
          departement.code_departement.toString().padStart(2, '0')
        )
      )
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
