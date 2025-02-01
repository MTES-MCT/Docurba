<template>
  <g>
    <path :style="lineStyle" :d="lineDrawer(points)" />
    <slot />
  </g>
</template>
<script>
import { scaleLinear, scaleTime } from 'd3'
import * as shapes from 'd3-shape'
import Layer from '@/components/Charts/Layer.js'

export default {
  name: 'VLine',
  mixins: [Layer],
  props: {
    curve: {
      type: String,
      default: 'curveLinear'
    }
  },
  data () {
    // console.log(this);

    // let xScale = scalePoint(),
    const xScale = this.isTime ? scaleTime() : scaleLinear()
    const yScale = scaleLinear()

    const yMax = this.getMax('y')

    const lineDrawer = shapes.line()
      .x(d => xScale(d.x))
      .y(d => yScale(d.y))
      // eslint-disable-next-line import/namespace
      .curve(shapes[this.curve])

    xScale.range([0, this.getWidth()])
    // xScale.domain(this.points.map(point => point.x));
    // xScale.padding(0.5);
    xScale.domain([this.getMin('x'), this.getMax('x')])

    yScale.range([this.getHeight(), 0])
    yScale.domain([this.getMin('y'), yMax])

    return {
      xScale,
      yScale,
      lineDrawer
    }
  },
  computed: {
    lineStyle () {
      return {
        stroke: this.color,
        fill: 'none',
        'stroke-width': '1.5px'
      }
    }
  }
}
</script>
