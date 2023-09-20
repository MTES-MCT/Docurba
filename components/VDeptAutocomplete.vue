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
    }
  },
  data () {
    const enrichedDepartements = departements.map(d => Object.assign({
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
        this.$emit('input', dept)
      }
    }
  }
}
</script>
