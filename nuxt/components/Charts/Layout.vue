<template>
  <svg :viewBox="'0 0 ' + width + ' ' + height">
    <g :transform="display">
      <slot />
    </g>
  </svg>
</template>
<script>
import { min, max, scaleOrdinal, interpolateRgbBasis, quantize } from 'd3'

export default {
  name: 'VChart',
  props: {
    isTime: {
      type: Boolean,
      default: false
    },
    height: {
      type: Number,
      default: 480
    },
    width: {
      type: Number,
      default: 720
    },
    left: {
      type: Number,
      default: 50
    },
    right: {
      type: Number,
      default: 50
    },
    top: {
      type: Number,
      default: 50
    },
    bottom: {
      type: Number,
      default: 50
    },
    collection: {
      type: Array,
      default () { return [] }
    },
    colors: {
      type: Array,
      default () {
        return ['rgb(12, 204, 249)', 'rgb(255, 18, 120)']
      }
    },
    xMin: {
      type: [Number, Object],
      default: null
    },
    xMax: {
      type: [Number, Object],
      default: null
    },
    yMin: {
      type: [Number, Object],
      default: null
    },
    yMax: {
      type: [Number, Object],
      default: null
    }
  },
  computed: {
    display () {
      return 'translate(' + this.left + ',' + this.top + ')'
    },
    _xMax () {
      return this.getMax('x')
    },
    _xMin () {
      return this.getMin('x')
    },
    _yMax () {
      return this.getMax('y')
    },
    _yMin () {
      return this.getMin('y')
    },
    colorScale () {
      if (this.colors && this.collection.length) {
        const colorInterpolator = interpolateRgbBasis(this.colors)

        const quantizeLength = this.collection.length === 1 ? 2 : this.collection.length

        return scaleOrdinal().domain(this.collection.map(dataset => dataset.label))
          .range(quantize(t => colorInterpolator(t), quantizeLength))
      } else { return undefined }
    }
  },
  methods: {
    getMax (axis) {
      let maxVal
      const fixed = typeof (this[axis + 'Max']) === 'number'

      if (fixed) {
        maxVal = this[axis + 'Max']
      } else if (this.collection && this.collection.length) {
        maxVal = max(this.collection.map(dataset => max(dataset.points, point => point[axis])))
      }

      return maxVal
    },
    getMin (axis) {
      let minVal
      const fixed = typeof (this[axis + 'Min']) === 'number'

      if (fixed) {
        minVal = this[axis + 'Min']
      } else if (this.collection && this.collection.length) {
        minVal = min(this.collection.map(dataset => min(dataset.points, point => point[axis])))
      }

      return minVal
    }
  }
}
</script>
