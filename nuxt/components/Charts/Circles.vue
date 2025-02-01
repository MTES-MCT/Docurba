<template>
  <g>
    <circle
      v-for="(point, i) in points"
      :key="`${point.x}-${i}`"
      :cx="center(point)[0]"
      :cy="center(point)[1]"
      :r="r"
      :fill="color"
      :style="poinStyle"
      @mouseover="$emit('hover', point)"
    />
    <slot />
  </g>
</template>
<script>
import { scaleLinear, scaleTime } from 'd3'
import Layer from '@/components/Charts/Layer.js'

export default {
  name: 'VPoints',
  mixins: [Layer],
  props: {
    r: {
      type: Number,
      default: 4
    },
    isMap: Boolean,
    pointer: Boolean
  },
  data () {
    const xScale = this.isTime ? scaleTime() : scaleLinear()
    const yScale = scaleLinear()

    xScale.range([0, this.getWidth()])
    xScale.domain([this.getMin('x'), this.getMax('x')])

    yScale.range([this.getHeight(), 0])
    yScale.domain([this.getMin('y'), this.getMax('y')])

    return {
      xScale,
      yScale
    }
  },
  computed: {
    poinStyle () {
      return {
        cursor: this.pointer ? 'pointer' : 'default'
      }
    }
  },
  methods: {
    center (point) {
      if (this.isMap) {
        return this.$parent.geoProjection([point.x, point.y])
      } else { return [this.xScale(point.x), this.yScale(point.y)] }
    }
  }
}
</script>
