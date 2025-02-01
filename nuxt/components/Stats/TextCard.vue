<template>
  <v-card flat color="bf100-g750" class="position-relative">
    <!-- <VFloatingShape src="/images/landing/circle_light_yellow.svg" :size="80" :right="floatingShape.right" :bottom="floatingShape.bottom" /> -->
    <v-card-title>
      <v-row no-gutters>
        <v-col cols="12">
          <v-icon color="focus">
            {{ icons.mdiInformationOutline }}
          </v-icon>
        </v-col>
        <v-col v-if="title">
          <b>{{ title }}</b>
        </v-col>
      </v-row>
    </v-card-title>
    <v-card-text class="black--text">
      <p>{{ text }}</p>
      <a v-if="action.link" :href="action.link" target="_blank" class="primary--text text-decoration-underline">
        <v-icon small color="primary">
          {{ icons.mdiArrowRight }}
        </v-icon>
        {{ action.text || action.link }}
      </a>
    </v-card-text>
  </v-card>
</template>

<script>
import { mdiInformationOutline, mdiArrowRight } from '@mdi/js'
export default {
  props: {
    title: {
      type: String,
      default: ''
    },
    text: {
      type: String,
      default: ''
    },
    action: {
      type: Object,
      default () { return {} }
    }
  },
  data () {
    return {
      icons: {
        mdiInformationOutline,
        mdiArrowRight
      },
      floatingShape: {
        right: Math.random() * 20,
        bottom: Math.random() * (-30)
      }
    }
  }
}
</script>
