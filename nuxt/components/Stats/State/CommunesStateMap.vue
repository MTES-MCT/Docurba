<template>
  <v-card flat class="stats-card" min-height="800px">
    <v-card-title>
      {{ title }}
    </v-card-title>
    <v-card-text v-if="topo">
      <ChartsLayout :height="700">
        <ChartsMap :topology="topo" features-key="a_com2022" color="rgb(255, 255, 255)" no-stroke>
          <ChartsMap :topology="topo" features-key="a_dep2022" color="rgb(0, 0, 0)" />
          <ChartsScales :scale="scale" :scale-points="scalePoints" transform="translate(0, -100)" />
        </ChartsMap>
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
import axios from 'axios'
import { groupBy } from 'lodash'

function scale (color) {
  return color
}

const colorMap = {
  '#2095CF': 'CC',
  '#8EC581': 'CC, PLU',
  '#7F5279': 'CC, PLUi',
  '#A88861': 'CC, PLU, PLUi',
  '#FBF432': 'PLU',
  '#EC812B': 'PLU, PLUi',
  '#DD0E23': 'PLUi'
}

export default {
  props: {
    title: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      scale,
      scalePoints: [],
      topo: null
    }
  },
  async mounted () {
    // This endpoint does not exist.
    // It's `/geojson/:locality` or `/topojson/:locality` in geo.js
    // Is it dead code?
    const { data: topojson } = await axios({
      url: '/api/geo/topojson/communes'
      // params: { codes: ['01001', '01002'] }
    })
    const { data: communesColors } = await axios('/json/communes_colors.json')

    console.log('communesColors', communesColors)
    console.log('topojson', topojson)

    const groupedTypes = groupBy(communesColors, c => c.color)

    Object.keys(groupedTypes).forEach((color) => {
      if (colorMap[color]) {
        this.scalePoints.push({
          value: color,
          label: `${colorMap[color]} : ${groupedTypes[color].length}`
        })
      }
    })

    topojson.objects.a_com2022.geometries.forEach((geometry) => {
      if (!geometry.properties) { geometry.properties = {} }

      const commune = communesColors.find(c => c.code === geometry.properties.codgeo)
      if (commune) {
        // console.log('set fill')
        geometry.properties.fill = commune.color
      }
    })

    this.topo = topojson
  }
}
</script>
