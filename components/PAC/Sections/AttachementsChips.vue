<template>
  <v-row>
    <v-col cols="12">
      <v-chip
        v-for="file in files"
        :key="file.name"
        class="mr-1 mb-1"
        color="primary"
        :href="file.url"
        target="_blank"
        :small="small"
      >
        {{ file.name }}
      </v-chip>
    </v-col>
  </v-row>
</template>

<script>
export default {
  props: {
    files: {
      type: Array,
      required: true
    },
    small: {
      type: Boolean,
      default: false
    }
  }
}
</script>
