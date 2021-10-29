<template>
  <v-card flat color="g100">
    <v-card-title class="break-word">
      {{ source.title }}
    </v-card-title>
    <v-row>
      <v-col v-if="source.subTheme" cols="12">
        <v-chip
          outlined
          class="text-capitalize"
          color="bf300 ml-4"
        >
          {{ source.subTheme }}
        </v-chip>
      </v-col>
      <v-col cols="12">
        <v-card-text>
          <nuxt-content :document="source" />
        </v-card-text>
      </v-col>
      <v-col v-if="regionSource && regionSource.charts" cols="12">
        <client-only>
          <ChartsLayout v-for="(chart, chartIndex) in regionSource.charts" :key="chartIndex">
            <ChartsMap
              :topology="require(`@/assets/data/${chart.data}`)"
              color="black"
              features-key="FRA"
              projection="geoConicConformal"
            >
            <!-- <ChartsMap :topology="borders" color="black" featuresKey="FRA_country"></ChartsMap> -->
            <!-- <v-points v-show="showCities" :points="cities" isMap v-on:hover="hoverPoint" pointer>
              </v-points> -->
            </ChartsMap>
          </ChartsLayout>
        </client-only>
      </v-col>
    </v-row>
    <v-card-actions>
      <v-row justify="end">
        <v-col v-if="regionSource && regionSource.source" cols="auto">
          <v-btn
            :href="regionSource.source"
            target="_blank"
            color="primary"
            outlined
          >
            Source regionale
            <v-icon class="ml-2" small>
              {{ icons.mdiOpenInNew }}
            </v-icon>
          </v-btn>
        </v-col>
        <v-col v-if="source.sourceNational" cols="auto">
          <v-btn
            :href="source.sourceNational"
            target="_blank"
            color="primary"
          >
            Source nationale
            <v-icon class="ml-2" small>
              {{ icons.mdiOpenInNew }}
            </v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mdiOpenInNew } from '@mdi/js'

export default {
  props: {
    source: {
      type: Object,
      required: true
    },
    region: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      icons: {
        mdiOpenInNew
      }
    }
  },
  computed: {
    regionSource () {
      if (this.region && this.source.regions && this.source.regions.length) {
        return this.source.regions.find((r) => {
          return r.iso === this.region
        })
      } else { return null }
    }
  }
}
</script>
