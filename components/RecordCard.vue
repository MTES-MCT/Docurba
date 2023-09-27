<template>
  <v-card flat outlined class="d-flex flex-column">
    <v-card-title class="break-word">
      {{ record.title }}
    </v-card-title>
    <v-card-text class="record-description">
      {{ record.description }}
    </v-card-text>
    <v-spacer />
    <v-card-actions>
      <v-btn
        depressed
        tile
        block
        color="primary"
        :href="record.url"
        target="_blank"
      >
        Voir la ressource
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  props: {
    record: {
      type: Object,
      required: true
    }
  }
}
</script>

<style>
.record-description {
  max-height: 200px;
  overflow-y: auto;
}
</style>
