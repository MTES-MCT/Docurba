<template>
  <v-card flat class="stats-card" min-height="200px" height="100%">
    <template v-if="points && points.length">
      <v-card-title class="break-word">
        {{ title }}
      </v-card-title>
      <v-card-text>
        <v-sparkline
          :value="points"
          color="primary"
          height="100"
          padding="12"
          stroke-linecap="round"
          line-width="2"
          smooth
        >
          <template #label="item">
            <tspan v-if="item.index === 0 || item.index === points.length-1">
              {{ points[item.index].label }}
            </tspan>
          </template>
        </v-sparkline>
      </v-card-text>
    </template>
    <v-card-text v-else>
      <v-row class="card-loader" justify="center" align="center">
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
  }
}
</script>
