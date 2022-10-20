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
        dense
        placeholder="EPCI"
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
    },
    epciList: {
      type: Array,
      default () {
        return []
      }
    }
  },
  data () {
    const items = this.epciList.length ? this.epciList : EPCIs
    const currentEPCI = items.find(e => e.EPCI === (this.value ? this.value.EPCI : null))

    return {
      selectedEpci: currentEPCI || null
    }
  },
  computed: {
    items () {
      return this.epciList.length ? this.epciList : EPCIs
    }
  },
  methods: {
    input () {
      this.$emit('input', this.selectedEpci)
    }
  }
}
</script>
