<template>
  <v-card outlined class="feature-card">
    <div class="floating-title focus--text text-h2 px-3">
      {{ floatingTitle }}
    </div>
    <v-card-title class="mt-4">
      <b>{{ title }}</b>
    </v-card-title>
    <v-card-text class="black--text">
      {{ text }}
    </v-card-text>
  </v-card>
</template>
<script>
export default {
  props: {
    floatingTitle: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: ''
    },
    text: {
      type: String,
      default: ''
    }
  }
}
</script>
<style scoped>
.feature-card {
  border-block-color: #ECECFE;
}

.floating-title {
position: absolute;
background-color: white;
top: -20px;
left: 16px;
}
</style>
