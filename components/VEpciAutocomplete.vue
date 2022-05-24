<template>
  <v-row>
    <v-col cols="12">
      <v-autocomplete
        v-model="selectedEpci"
        no-data-text="Selectionnez un EPCI"
        :items="items"
        item-text="label"
        return-object
        hide-details
        filled
        label="EPCI"
        @change="input"
      />
    </v-col>
  </v-row>
</template>

<script>
// import axios from 'axios'
import EPCIs from '@/assets/data/EPCI_no_towns.json'

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
    const currentEPCI = EPCIs.find(e => e.id === this.value ? this.value.id : '')

    return {
      selectedEpci: currentEPCI || null,
      items: EPCIs
    }
  },
  methods: {
    input () {
      console.log(this.selectedEpci)
      this.$emit('input', this.selectedEpci)
    }
  }
}
</script>
