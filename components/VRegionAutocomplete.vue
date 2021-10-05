<template>
  <v-autocomplete
    :items="regions"
    item-text="name"
    return-object
    hide-details
    filled
    placeholder="Territoire"
    @change="input"
  /></v-autocomplete>
</template>

<script>
import regions from '@/assets/data/Regions.json'
export default {
  data () {
    return {
      regions
    }
  },
  methods: {
    input (region) {
      this.$emit('input', region)
    }
  }
}
</script>
