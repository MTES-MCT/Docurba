<template>
  <v-row>
    <v-col v-show="!hideDept" cols="12" :md="colsDep">
      <v-autocomplete
        v-model="selectedDepartement"
        v-bind="inputProps"
        :items="departements"
        placeholder="Departement"
        hide-details
        filled
        autocomplete="off"
        return-object
        :dense="!large"
        @blur="$emit('blur')"
        @change="fetchCollectivites"
      />
    </v-col>
    <v-col cols="12" :md="colsTown">
      <validation-provider v-slot="{ errors }" name="Collectivité" rules="requiredCollectivite">
        <v-autocomplete
          v-model="selectedCollectivite"
          v-bind="inputProps"
          hide-details
          :no-data-text="loading ? 'Chargement ...' : 'Selectionnez un département'"
          :items="collectivites"
          item-text="name"
          autocomplete="off"
          :error-messages="errors"
          return-object
          filled
          placeholder="Commune ou EPCI"
          :loading="loading"
          :dense="!large"
        />
      </validation-provider>
    </v-col>
  </v-row>
</template>

<script>
import axios from 'axios'
import { ValidationProvider } from 'vee-validate'
import FormInput from '@/mixins/FormInput.js'
import departements from '@/assets/data/departements-france.json'

export default {
  name: 'VCollectiviteAutocomplete',
  components: {
    ValidationProvider
  },
  mixins: [FormInput],
  props: {
    large: {
      type: Boolean,
      default: false
    },
    value: {
      type: Object,
      default: () => null
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
        // eslint-disable-next-line
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
  watch: {
    selectedCollectivite () {
      this.$emit('input', this.selectedCollectivite)
    }
  },
  async mounted () {
    await this.fetchCollectivites()
    if (this.value) {
      this.selectedCollectivite = this.collectivites.find((e) => {
        return e?.EPCI?.toString() === this.value.collectivite_id || e?.code_commune_INSEE?.toString() === this.value.collectivite_id
      })
    }
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
