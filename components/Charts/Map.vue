<template>
  <g>
    <path v-for="(feature, i) in features" :key="i" :d="geoDrawer(feature)" :style="pathStyle(feature)" :fill="feature.properties.fill || 'none'" />
    <slot v-bind="{geoProjection}" />
  </g>
</template>
<script>
import { geoPath } from 'd3'
import * as projections from 'd3-geo'

import * as topojson from 'topojson-client'
import Layer from '@/components/Charts/Layer.js'

export default {
  name: 'VMap',
  mixins: [Layer],
  props: {
    topology: {
      type: Object,
      required: true
    },
    projection: {
      type: String,
      default: 'geoMercator'
    },
    featuresKey: {
      type: String,
      required: true
    }
  },
  data () {
    // eslint-disable-next-line import/namespace
    const geoProjection = this.$parent.geoProjection || projections[this.projection]()
    const geoDrawer = geoPath()

    if (!this.$parent.geoProjection) {
      if (this.topology.transform) {
        geoProjection.scale(this.topology.transform.scale)
      }
      geoProjection.fitSize([this.getWidth(), this.getHeight()], this.getFeatures())
    }

    geoDrawer.projection(geoProjection)

    return {
      geoDrawer,
      geoProjection,
      features: this.getFeatures().features,
      isMap: true
    }
  },
  computed: {
    mapStyle () {
      return {
        stroke: this.color,
        fill: 'none',
        'stroke-width': '1px'
      }
    }
  },
  watch: {
    // width () {
    //   if (!this.$parent.geoProjection) {
    //     this.geoProjection.fitSize([this.getWidth(), this.getHeight()], this.getFeatures())
    //   }
    //   this.$forceUpdate()
    // },
    // height () {
    //   if (!this.$parent.geoProjection) {
    //     this.geoProjection.fitSize([this.getWidth(), this.getHeight()], this.getFeatures())
    //   }
    //   this.$forceUpdate()
    // }
  },
  methods: {
    getFeatures () {
      // console.log(topojson.feature(this.topology, this.featuresKey))
      return topojson.feature(this.topology, this.featuresKey)
    },
    pathStyle (feature) {
      return {
        stroke: this.color,
        fill: feature.properties ? feature.properties.fill : '',
        'stroke-width': '0.5px'
      }
    }
  }
}
</script>
