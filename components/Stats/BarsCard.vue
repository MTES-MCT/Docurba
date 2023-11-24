<template>
  <v-card flat class="stats-card" min-height="200px" max-height="350px">
    <v-card-title>
      {{ title }}
    </v-card-title>
    <v-card-text v-if="Object.keys(points).length" class="d-flex justify-center">
      <ChartsLayout :height="300" class="bars-layout">
        <ChartsBars :points="points" :y-min="0" color="#9a9aff">
          <ChartsLabels axis="y" text="yLabel" />
          <!-- <ChartsAxis axis="y" /> -->
          <ChartsLabels axis="x" text="xLabel" />
        </ChartsBars>
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
<style scoped>
.bars-layout {
  max-height: 300px;
}
</style>
