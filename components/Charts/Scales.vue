<template>
  <g>
    <g v-for="(tick, i) in ticks" :key="tick.value">
      <rect
        :fill="scale(tick.value)"
        :x="getX(i)"
        :y="getY(i)"
        :width="20"
        :height="15"
      />
      <text
        :x="getX(i) + 23"
        :y="getY(i) + 12"
        :text-anchor="'start'"
      >
        {{ tick.label }}
      </text>
    </g>
  </g>
</template>
<script>
import Layer from '@/components/Charts/Layer.js'

export default {
  name: 'VAxis',
  mixins: [Layer],
  props: {
    scale: {
      type: [Object, Function],
      required: true
    },
    scalePoints: {
      type: Array,
      default () { return [] }
    },
    top: {
      type: Boolean,
      default: false
    },
    bottom: {
      type: Boolean,
      default: true
    },
    right: {
      type: Boolean,
      default: false
    },
    left: {
      type: Boolean,
      default: true
    }
  },
  data () {
    const max = this.scale.domain()[1]
    const quarter = max / 4

    // console.log('scales', this.scale.domain(), this.scale.range())

    return {
      ticks: this.scalePoints.length
        ? this.scalePoints
        : [
            { value: quarter, label: `${Math.round(quarter)}` },
            { value: quarter * 2, label: `${Math.round(quarter * 2)}` },
            { value: quarter * 3, label: `${Math.round(quarter * 3)}` },
            { value: max, label: `${max}` }
          ]
    }
  },
  methods: {
    getX (index) {
      if (this.right) {
        return this.getWidth() - 20
      } else { return 0 }
    },
    getY (index) {
      return this.getHeight() - (index * 22)
    }
  }
}
</script>
