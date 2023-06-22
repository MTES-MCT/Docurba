import { min, max } from 'd3'

// @vue/component
export default {
  props: {
    points: {
      type: Array,
      default () { return [] }
    },
    label: {
      type: String,
      default: ''
    },
    isTime: {
      type: Boolean,
      default () {
        return this.$parent.isTime || false
      }
    },
    xMin: {
      type: [Number, Date, String],
      default () {
        return this.$parent._xMin
      }
    },
    xMax: {
      type: [Number, Date, String],
      default () {
        return this.$parent._xMax
      }
    },
    yMin: {
      type: Number,
      default () {
        return this.$parent._yMin
      }
    },
    yMax: {
      type: Number,
      default () {
        return this.$parent._yMax
      }
    },
    color: {
      type: String,
      default () {
        if (this.$parent.colorScale && this.label) {
          return this.$parent.colorScale(this.label)
        } else { return 'rgb(12, 204, 249)' }
      }
    }
  },
  computed: {
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
    width () {
      return this.getWidth()
    },
    height () {
      return this.getHeight()
    }
  },
  watch: {
    _xMax () {
      if (this.xScale) { this.xScale.domain([this._xMin, this._xMax]) }
      this.$forceUpdate()
    },
    _xMin () {
      if (this.xScale) { this.xScale.domain([this._xMin, this._xMax]) }
      this.$forceUpdate()
    },
    _yMax () {
      if (this.yScale) { this.yScale.domain([this._yMin, this._yMax]) }
      this.$forceUpdate()
    },
    _yMin () {
      if (this.yScale) { this.yScale.domain([this._yMin, this._yMax]) }
      this.$forceUpdate()
    },
    width () {
      if (this.xScale) {
        this.xScale.range([0, this.width])
        this.$forceUpdate()
      }
    },
    height () {
      if (this.yScale) {
        this.yScale.range([this.height, 0])
        this.$forceUpdate()
      }
    }
  },
  methods: {
    getWidth () {
      return this.$parent.width - (this.$parent.right || 0) - (this.$parent.left || 0)
    },
    getHeight () {
      return this.$parent.height - (this.$parent.top || 0) - (this.$parent.bottom || 0)
    },
    getMax (axis) {
      if (!this.isMap) {
        if (this.isNumber(this.$parent['_' + axis + 'Max'])) { return this.$parent['_' + axis + 'Max'] }

        let fixed = typeof (this[axis + 'Max']) === 'number'
        if (!fixed && this[axis + 'Max']) { fixed = this[axis + 'Max'].constructor.name === 'Date' }

        if (!fixed) {
          let maxVal = max(this.points, point => point[axis])
          if (this.isTime && axis !== 'y') { maxVal = new Date(maxVal) }

          return maxVal
        } else { return this[axis + 'Max'] }
      } else { return 0 }
    },
    getMin (axis) {
      if (!this.isMap) {
        if (this.isNumber(this.$parent['_' + axis + 'Min'])) { return this.$parent['_' + axis + 'Min'] }

        let fixed = typeof (this[axis + 'Min']) === 'number'
        if (!fixed && this[axis + 'Min']) { fixed = this[axis + 'Min'].constructor.name === 'Date' }

        if (!fixed) {
          let minVal = min(this.points, point => point[axis])
          if (this.isTime) { minVal = new Date(minVal) }

          return minVal
        } else { return this[axis + 'Min'] }
      } else { return 0 }
    },
    positiveOrZero (nb) {
      return nb > 0 ? nb : 0
    },
    isNumber (nb) {
      return typeof (nb) === 'number'
    }
  }
}
