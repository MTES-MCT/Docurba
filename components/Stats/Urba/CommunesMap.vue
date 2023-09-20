<template>
  <v-card flat class="stats-card" min-height="400px">
    <v-card-title>
      {{ title }}
    </v-card-title>
    <v-card-text v-if="topo">
      <ChartsLayout>
        <ChartsMap :topology="topo" features-key="a_com2022" color="rgb(255, 255, 255)">
          <ChartsMap :topology="topo" features-key="a_dep2022" color="rgb(0, 0, 0)" />
          <ChartsScales :scale="colorScale" :scale-points="scalePoints" />
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
import {
  // scaleLinear,
  scaleOrdinal,
  schemeCategory10
  // interpolateRgbBasis, quantize
} from 'd3'

import axios from 'axios'

const docTypes = {
  RNU: 0,
  CC: 1,
  PLU: 2,
  PLUiS: 3,
  PLUi: 4
}

export default {
  props: {
    title: {
      type: String,
      default: ''
    }
  },
  data () {
    const colorScale = scaleOrdinal(schemeCategory10).domain(Object.values(docTypes))

    return {
      // newTopo,
      topo: null,
      colorScale,
      scalePoints: Object.keys(docTypes).map((type) => {
        const val = docTypes[type]
        return { value: val, label: type }
      })
    }
  },
  async mounted () {
    const { data: topojson } = await axios('/api/geo/topojson/communes')
    const { data: collectivites } = await axios('/api/urba/documents/collectivites')

    // console.log(collectivites, topojson.objects.a_com2022.geometries)

    topojson.objects.a_com2022.geometries.forEach((geometry) => {
      if (!geometry.properties) { geometry.properties = {} }

      const collectivite = collectivites.find(c => c.code === geometry.properties.codgeo)
      if (collectivite) {
        // console.log('set fill')
        geometry.properties.fill = this.colorScale(docTypes[collectivite.docType] || 0)
      }
    })

    this.topo = topojson
  }
}
</script>
