<template>
  <v-row>
    <v-col v-show="!hideDept" cols="12" :md="colsDep">
      <v-autocomplete
        v-model="selectedDepartement"
        v-bind="inputProps"
        :items="departements"
        placeholder="Departement"
        hide-details
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
          item-text="intitule"
          autocomplete="off"
          :error-messages="errors"
          return-object
          :filter="customFilter"
          placeholder="Commune ou EPCI"
          :loading="loading"
          :dense="!large"
        />
      </validation-provider>
    </v-col>
  </v-row>
</template>

<script>
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
    const enrichedDepartements = departements.map(d => ({
      ...d,
      text: `${d.nom_departement} - ${d.code_departement}`,
      code_departement: d.code_departement.toString().padStart(2, '0')
    }))
    let defaultDepartement = null

    if (this.defaultDepartementCode) {
      defaultDepartement = enrichedDepartements.find((d) => {
        return d.code_departement.toString() === this.defaultDepartementCode
      })
    }
    return {
      selectedDepartement: defaultDepartement,
      selectedCollectivite: { ...this.value },
      departements: enrichedDepartements,
      collectivites: (this.value && this.value.name) ? [{ ...this.value }] : [],
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
      this.selectedCollectivite = this.collectivites.find(e => e.code === this.value.code)
    }
  },
  methods: {
    customFilter (item, search, value) {
      if (search?.length === 0 || value?.length === 0) { return true }
      const normalizedValue = value.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
      const normalizedSearch = search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return normalizedValue.includes(normalizedSearch)
    },
    async fetchCollectivites () {
      if (this.selectedDepartement) {
        this.loading = true
        try {
          const groupements = await this.$djangoApi.get('/collectivites/', {
            departement: this.selectedDepartement.code_departement,
            exclude_communes: true,
            competence: 'plan',
            // eslint-disable-next-line no-dupe-keys
            competence: 'schema'
          })
          const communes = await this.$djangoApi.get('/communes/', {
            departement: this.selectedDepartement.code_departement,
            type: 'COM'
          })
          const BANATIC_EPCI_TYPES = ['CA', 'CC', 'CU', 'METRO', 'MET69']
          const epcis = groupements.filter(e => BANATIC_EPCI_TYPES.includes(e.type))
          const autres = groupements.filter(e => !BANATIC_EPCI_TYPES.includes(e.type))
          this.collectivites = [{ header: 'Groupements' }, ...autres, { divider: true },
            { header: 'EPCI' }, ...epcis, { divider: true },
            { header: 'Communes' }, ...communes]
          this.loading = false
        } catch (error) {
          console.log(error)
        }
      }
    }
  }
}
</script>
