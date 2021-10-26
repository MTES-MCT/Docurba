<template>
  <v-select
    v-model="selectedDoc"
    filled
    hide-details
    placeholder="Type de document"
    :label="label"
    :items="documents"
  />
</template>

<script>
export default {
  props: {
    value: {
      type: String,
      required: true
    },
    label: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      documents: ['CC', 'PLU', 'PLUi', 'PLUi-H', 'PLUi-D', 'PLUi-HD', 'SCoT', 'SCot-AEC']
    }
  },
  computed: {
    selectedDoc: {
      get () {
        return this.value
      },
      set (val) {
        this.$emit('input', val)
      }
    }
  }
}
</script>
