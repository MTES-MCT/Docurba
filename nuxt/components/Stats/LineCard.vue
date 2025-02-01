<template>
  <v-card flat class="stats-card" min-height="200px" max-height="350px">
    <v-card-title>
      {{ title }}
    </v-card-title>
    <v-card-text v-if="Object.keys(points).length">
      <ChartsLayout :height="300">
        <ChartsLine :points="points" is-time :y-min="0" color="#9a9aff">
          <ChartsAxis axis="x" />
          <ChartsAxis axis="y" />
          <!-- <ChartsLabels axis="x" text="xLabel" /> -->
        </ChartsLine>
      </ChartsLayout>
    </v-card-text>
    <v-card-text v-else>
      <v-row justify="center" align="center">
        <v-progress-circular color="primary" indeterminate />
      </v-row>
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
    points: {
      type: Array,
      default () { return [] }
    }
  },
  data () {
    return {}
  }
}
</script>
