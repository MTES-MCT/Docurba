<template>
  <v-card flat class="stats-card">
    <v-card-title class="break-word">
      {{ title }}
    </v-card-title>
    <v-card-text class="text-center primary--text py-16">
      <v-progress-circular
        v-if="number || number === 0"
        :rotate="-90"
        :size="100"
        :width="15"
        :value="number"
      >
        {{ number }}
      </v-progress-circular>
      <v-progress-circular v-else color="primary" indeterminate />
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: ''
    },
    number: {
      type: [Number, String],
      default: ''
    }
  }
}
</script>

<style scoped>
.big-number {
  font-size: 64px;
}
</style>
