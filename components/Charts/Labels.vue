<template>
  <g>
    <g v-for="point in labels" :key="point.x" :transform="getLabelPosition(point)">
      <text :x="textAnchor == 'start' ? 10 : 0" :y="textAnchor == 'start' ? 5 : -5" :text-anchor="textAnchor">
        {{ point[text] }}
      </text>
    </g>
  </g>
</template>
<script>
import { scaleLinear, scaleTime } from 'd3'
import Layer from '@/components/Charts/Layer.js'

export default {
  name: 'VLabels',
  mixins: [Layer],
  props: {
    axis: {
      type: String,
      required: true
    },
    text: {
      type: String,
      default: 'label'
    },
    textAnchor: {
      type: String,
      default: 'middle'
    }
  },
  computed: {
    xScale () {
      const parentScale = this.getParentScale('x')

      if (!parentScale) {
        const scale = this.isTime ? scaleTime() : scaleLinear()

        scale.range([0, this.getWidth()])
        scale.domain([this.getMin('x'), this.getMax('x')])

        return scale
      } else { return parentScale }
    },
    yScale () {
      const parentScale = this.getParentScale('y')

      if (!parentScale) {
        const scale = scaleLinear()

        scale.range([this.getHeight(), 0])
        scale.domain([this.getMin('y'), this.getMax('y')])

        return scale
      } else { return parentScale }
    },
    labels () {
      if (this.$parent.collection) {
        return this.$parent.collection.map((d) => {
          return {
            x: this._xMax,
            y: d.points[d.points.length - 1].y,
            label: d.label
          }
        })
      } else { return this.$parent.points }
    }
  },
  methods: {
    getParentScale (axis) {
      return this.$parent[axis + 'Scale']
    },
    getLabelPosition (point) {
      // console.log('Get Label Position');
      let xMargin = 0

      if (this.xScale.bandwidth) {
        xMargin = this.xScale.bandwidth() / 2
      }

      const x = this.xScale(point.x) + xMargin
      const y = this.axis === 'y' ? this.yScale(point.y) : this.getHeight() + 20

      return `translate(${x}, ${y})`
    }
  }
}
</script>
