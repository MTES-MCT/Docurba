<template>
  <v-autocomplete
    :items="regions"
    item-text="name"
    return-object
    hide-details
    filled
    placeholder="Territoire"
    :label="label"
    @change="input"
  />
</template>

<script>
import regions from '@/assets/data/Regions.json'
export default {
  props: {
    value: {
      type: [String, Object],
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    returnIso: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      regions
    }
  },
  methods: {
    input (region) {
      this.$emit('input', this.returnIso ? region.iso : region)
    }
  }
}
</script>
