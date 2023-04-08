<template>
  <v-card flat outlined>
    <v-toolbar flat>
      <v-toolbar-title>
        {{ label }}
      </v-toolbar-title>
    </v-toolbar>
    <v-card-text class="pt-3">
      <nuxt-content class="pac-section-content" :document="diff" />
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  props: {
    diff: {
      type: Object,
      required: true
    },
    label: {
      type: String,
      default: ''
    }
  }
}
</script>
