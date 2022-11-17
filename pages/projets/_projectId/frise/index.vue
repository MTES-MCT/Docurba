<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          Feuille de route partagée
        </h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="8">
        <v-card outlined>
          <v-card-text>
            <FriseDocTimeline />
          </v-card-text>
        </v-card>
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
