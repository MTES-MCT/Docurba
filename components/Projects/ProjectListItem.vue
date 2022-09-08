<template>
  <v-hover v-slot="{hover}">
    <v-list-item
      :to="`/projets/${project.id}/content`"
      nuxt
      two-line
      @click="$emit('input', false)"
    >
      <v-list-item-content>
        <v-list-item-title>{{ project.name }}</v-list-item-title>
        <v-list-item-subtitle>{{ project.docType }}</v-list-item-subtitle>
      </v-list-item-content>
      <v-list-item-action>
        <v-btn
          v-show="hover && shareable"
          depressed
          tile
          icon
          @click.prevent.stop="$emit('share', project)"
        >
          <v-icon>{{ icons.mdiShare }}</v-icon>
        </v-btn>
      </v-list-item-action>
    </v-list-item>
  </v-hover>
</template>

<script>
import { mdiShare } from '@mdi/js'

export default {
  props: {
    project: {
      type: Object,
      required: true
    },
    shareable: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      icons: {
        mdiShare
      }
    }
  }
}
</script>
