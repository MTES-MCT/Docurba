<script>
export default {
  props: {
    id: {
      default: undefined,
      type: String,
    },
    value: {
      default: '',
      type: String,
    },
  },
  data() {
    return {
      departments: [],
    }
  },
  computed: {
    options() {
      return this.departments.map((department) => ({
        label: `${department.name} - ${department.code}`,
        value: department.code,
      }))
    },
  },
  async created() {
    this.departments = await this.$store.dispatch('department/list')
  },
}
</script>

<template>
  <FRFieldAutocomplete :id="id"
                       :options="options"
                       placeholder="Département"
                       :value="value"
                       @input="$emit('input', $event)" />
</template>
