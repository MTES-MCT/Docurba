<template>
  <v-toolbar-items v-if="!dense">
    <v-btn
      depressed
      tile
      icon
      @click="
        editor
          .chain()
          .focus()
          .toggleBold()
          .run()
      "
    >
      <v-icon>{{ icons.mdiFormatBold }}</v-icon>
    </v-btn>
    <v-btn
      depressed
      tile
      icon
      @click="
        editor
          .chain()
          .focus()
          .toggleItalic()
          .run()
      "
    >
      <v-icon>{{ icons.mdiFormatItalic }}</v-icon>
    </v-btn>
    <v-btn
      depressed
      tile
      icon
      @click="
        editor
          .chain()
          .focus()
          .toggleUnderline()
          .run()
      "
    >
      <v-icon>{{ icons.mdiFormatUnderline }}</v-icon>
    </v-btn>
    <v-btn
      depressed
      tile
      icon
      @click="
        editor
          .chain()
          .focus()
          .toggleBulletList()
          .run()
      "
    >
      <v-icon>{{ icons.mdiFormatListBulleted }}</v-icon>
    </v-btn>
    <v-btn
      depressed
      tile
      icon
      @click="
        editor
          .chain()
          .focus()
          .toggleOrderedList()
          .run()
      "
    >
      <v-icon>{{ icons.mdiFormatListNumbered }}</v-icon>
    </v-btn>
  </v-toolbar-items>
</template>

<script>
import {
  mdiFormatBold, mdiFormatUnderline, mdiFormatItalic,
  mdiFormatListBulleted, mdiFormatListNumbered
} from '@mdi/js'

export default {
  props: {
    editor: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiFormatBold,
        mdiFormatUnderline,
        mdiFormatItalic,
        mdiFormatListBulleted,
        mdiFormatListNumbered
      }
    }
  }
}
</script>
