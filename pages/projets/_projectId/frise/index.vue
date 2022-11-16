<template>
  <v-container>
    <v-row>
      <v-col cols="8">
        <FriseDocTimeline />
      </v-col>
    </v-row>
  </v-container>
  <!-- <VGlobalLoader v-else /> -->
</template>

<script>
export default {
  data () {
    return {
      loaded: true
    }
  }
}
</script>
