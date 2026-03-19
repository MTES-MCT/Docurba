<template>
  <span v-if="topicsToDisplay">
    <v-chip
      v-for="topic in topicsToDisplay"
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
  },
  computed: {
    topicsToDisplay () {
      return this.topics.filter(e => e !== 'Autre')
    }
  }
}
</script>

<style scoped>
.v-chip:hover:before {
    opacity: 0;
}
</style>
