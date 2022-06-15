<template>
  <v-container>
    <v-row class="page-container" justify="center" align="center">
      <v-col class="text-center">
        <h1>{{ project.name }}</h1>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  props: {
    project: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: calc(293mm - 50mm - 135px);
  /* min-height: calc(250mm - 140px); */
  /* min-height: 297mm; */
  /* page-break-inside: avoid; */
}
</style>
