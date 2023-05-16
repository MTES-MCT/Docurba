<template>
  <v-card flat class="stats-card" min-height="200px">
    <v-card-title>
      {{ title }}
    </v-card-title>
    <v-card-text v-if="Object.keys(points).length">
      <ChartsLayout>
        <ChartsMap :topology="newTopo" features-key="FRA" color="rgb(0, 0, 0)" />
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
import { max, scaleOrdinal, interpolateRgbBasis, quantize } from 'd3'
import franceDepts from '@/assets/data/GeoJSON/FRA.json'

export default {
  props: {
    title: {
      type: String,
      default: ''
    },
    points: {
      type: Object,
      default () { return {} }
    }
  },
  data () {
    const values = Object.values(this.points)
    const maxValue = max(values)
    const colorInterpolator = interpolateRgbBasis(['rgb(255, 255, 255)', 'rgb(0, 0, 145)'])

    // console.log(quantize(t => colorInterpolator(t), maxValue))

    const colorScale = scaleOrdinal().domain(Array.from(Array(maxValue + 1).keys()))
      .range(quantize(t => colorInterpolator(t), maxValue + 1))

    // This code is maybe not optimal but it's here to avoid sharing references on .fill
    const newTopo = Object.assign({}, franceDepts)

    newTopo.objects.FRA.geometries = newTopo.objects.FRA.geometries.map((geometry) => {
      const newGeometry = Object.assign({}, geometry)

      if (geometry.properties && geometry.properties.adm1_code) {
        newGeometry.properties = Object.assign({}, geometry.properties)

        const dept = newGeometry.properties.iso_3166_2.replace('FR-0', '').replace('FR-', '')
        newGeometry.properties.fill = colorScale(this.points[dept])
      }

      return newGeometry
    })

    return {
      newTopo
    }
  }
}
</script>
