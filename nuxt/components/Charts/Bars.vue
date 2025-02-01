<template>
  <g>
    <rect
      v-for="point in points"
      :key="point.x"
      :fill="color"
      :x="xScale(point.x)"
      :y="yScale(point.y)"
      :width="xScale.bandwidth()"
      :height="positiveOrZero(getHeight() - yScale(point.y))"
    />
    <slot />
  </g>
</template>
<script>
import { scaleLinear, scaleBand } from 'd3'
import Layer from '@/components/Charts/Layer.js'

export default {
  name: 'VBars',
  mixins: [Layer],
  data () {
    const xScale = scaleBand()
    const yScale = scaleLinear()

    // let yMax = this.getMax('y');

    xScale.range([0, this.getWidth()])
    xScale.domain(this.points.map(point => point.x))
    xScale.padding(0.2)

    yScale.range([this.getHeight(), 0])
    yScale.domain([this.getMin('y'), this.getMax('y')])

    return {
      xScale,
      yScale
    }
  }
}
</script>
