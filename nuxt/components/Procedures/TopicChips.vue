<template>
  <span v-if="topics">
    <v-chip
      v-for="topic in topics"
      :key="topic"
      color="blue"
      outlined
      class="mr-2"
      :small="small"
    >
      {{ topic }}
    </v-chip>
  </span>
</template>

<script>
export default {
  props: {
    topics: {
      type: Array,
      required: true
    },
    small: {
      type: Boolean,
      required: false
    }
  }
}
</script>
