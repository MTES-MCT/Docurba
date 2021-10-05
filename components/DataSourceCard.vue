<template>
  <v-card flat color="g100">
    <v-card-title>
      {{ source.title }}
    </v-card-title>
    <v-row v-if="source.subTheme">
      <v-col cols="12">
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
    </v-row>
    <v-card-actions>
      <v-row justify="end">
        <v-col v-if="regionSource" cols="auto">
          <v-btn
            :href="regionSource.source"
            target="_blank"
            color="primary"
            outlined
          >
            Source regional
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
            Source national
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
