<template>
  <g>
    <line
      :x1="0"
      :x2="axis === 'x' ? getWidth() : 0"
      :y1="getHeight()"
      :y2="axis === 'y' ? 0 : getHeight()"
      stroke="black"
    />
    <g
      v-for="(tick, i) in ticks()"
      :key="i"
      :transform="getTickPosition(tick)"
    >
      <line
        :x1="0"
        :x2="axis === 'x' ? 0 : -5"
        :y1="0"
        :y2="axis === 'y' ? 0 : 5"
        stroke="black"
      />
      <text
        :x="axis === 'x' ? 0 : -7"
        :y="axis === 'y' ? 5 : 20"
        :text-anchor="axis === 'x' ? 'middle' : 'end'"
      >
        {{ isTime ? ticksFormat(tick) : tick }}
      </text>
    </g>
  </g>
</template>
<script>
import { scaleLinear, scaleTime } from 'd3'
import Layer from '@/components/Charts/Layer.js'

export default {
  name: 'VAxis',
  mixins: [Layer],
  props: {
    axis: {
      type: String,
      required: true
    }
  },
  data () {
    let scale = this.getParentScale()

    if (!scale) {
      scale = this.isTime ? scaleTime() : scaleLinear()

      if (this.axis === 'x') {
        scale.range([0, this.getWidth()])
      } else { scale.range([this.getHeight(), 0]) }

      scale.domain([this.getMin(this.axis), this.getMax(this.axis)])
    }

    return {
      scale,
      ticksFormat: scale.tickFormat ? scale.tickFormat() : undefined
    }
  },
  watch: {
    _xMax () { this.updateDomain() },
    _xMin () { this.updateDomain() },
    _yMax () { this.updateDomain() },
    _yMin () { this.updateDomain() }
  },
  methods: {
    getParentScale () {
      return this.$parent[this.axis + 'Scale']
    },
    getTickPosition (tick) {
      let margin = 0

      if (this.scale.bandwidth) {
        margin = this.scale.bandwidth() / 2
      }

      const x = this.axis === 'x' ? this.scale(tick) + margin : 0
      const y = this.axis === 'y' ? this.scale(tick) : this.getHeight()

      return `translate(${x}, ${y})`
    },
    ticks () {
      if (this.scale.ticks) {
        return this.scale.ticks()
      } else { return this.scale.domain() }
    },
    updateDomain () {
      if (!this.getParentScale()) {
        this.scale.domain([this.getMin(this.axis), this.getMax(this.axis)])
      }

      if (this.scale.ticksFormat) { this.ticksFormat = this.scale.ticksFormat() }
      this.$forceUpdate()
    }
  }
}
</script>
