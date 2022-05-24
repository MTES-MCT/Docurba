<template>
  <v-row>
    <v-col cols="12">
      <!-- <v-autocomplete
        :value="selectedTown"
        no-data-text="Selectionnez un département"
        :items="towns"
        item-text="nom_commune"
        return-object
        hide-details
        filled
        label="Commune"
        @change="input"
      /> -->
    </v-col>
  </v-row>
</template>

<script>
// import axios from 'axios'
// import EPCIs from '@/assets/data/EPCI_no_towns.json'

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
    return {

    }
  }
}
</script>
