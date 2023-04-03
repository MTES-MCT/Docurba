<template>
  <v-row>
    <v-col v-show="!hideDept" cols="12" :sm="colsDep">
      <v-autocomplete
        v-model="selectedDepartement"
        v-bind="inputProps"
        :items="departements"
        placeholder="Departement"
        hide-details
        filled
        return-object
        dense
        @change="fetchCollectivites"
      />
    </v-col>
    <v-col cols="12" :sm="colsTown">
      <v-autocomplete
        :value="selectedCollectivite"
        v-bind="inputProps"
        :no-data-text="loading ? 'Chargement ...' : 'Selectionnez un département'"
        :items="collectivites"
        item-text="name"
        return-object
        hide-details
        filled
        placeholder="Commune ou EPCI"
        :loading="loading"
        dense
        @change="$emit('input', arguments[0])"
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
    inputProps: {
      type: Object,
      default () { return {} }
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
      selectedCollectivite: Object.assign({}, this.value),
      departements: enrichedDepartements,
      collectivites: (this.value && this.value.name) ? [Object.assign({}, this.value)] : [],
      loading: false
    }
  },
  mounted () {
    this.fetchCollectivites()
  },
  methods: {
    async fetchCollectivites () {
      if (this.selectedDepartement) {
        this.loading = true
        let towns = (await axios({
          url: '/api/communes',
          method: 'get',
          params: { departements: this.selectedDepartement.code_departement }
        })).data

        let epcis = (await axios({
          url: '/api/epci',
          method: 'get',
          params: { departement: this.selectedDepartement.code_departement }
        })).data

        epcis = epcis.map(e => ({ name: e.label, ...e, departement: this.selectedDepartement.code_departement, type: 'epci' }))
        towns = towns.map(e => ({ name: e.nom_commune_complet, departement: this.selectedDepartement.code_departement, type: 'commune', ...e }))
        this.collectivites = [{ header: 'ECPI' }, ...epcis, { divider: true }, { header: 'Communes' }, ...towns]
        this.loading = false
      }
    }
  }
}
</script>
