<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <p class="text-h2">
          Import des évènements Sudocu
        </p>
        <VTownAutocomplete v-model="selectedTown" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <FriseDocTimeline :events="events" />
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
export default {
  name: 'Sudocu',
  data () {
    return {
      selectedTown: null,
      events: []
    }
  },
  computed: {
    formatEvents () {
      return true
    }
  }
}
</script>
