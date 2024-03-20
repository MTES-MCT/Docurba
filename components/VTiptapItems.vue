<template>
  <v-toolbar-items>
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
          .toggleHighlight()
          .run()
      "
    >
      <v-icon>{{ icons.mdiFormatColorHighlight }}</v-icon>
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
    <v-btn
      depressed
      tile
      icon
      @click="
        editor
          .chain()
          .focus()
          .setColumns(2, true)
          .run()
      "
    >
      <v-icon>{{ icons.mdiFormatColumns }}</v-icon>
    </v-btn>
    <v-btn
      depressed
      tile
      icon
      @click="
        editor
          .chain()
          .focus()
          .unsetColumns()
          .run()
      "
    >
      <v-icon>{{ icons.mdiFormatAlignJustify }}</v-icon>
    </v-btn>

    <v-btn depressed tile icon @click="editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()">
      <v-icon>{{ icons.mdiTablePlus }}</v-icon>
    </v-btn>
  </v-toolbar-items>
</template>

<script>
import {
  mdiFormatBold, mdiFormatUnderline, mdiFormatItalic,
  mdiFormatListBulleted, mdiFormatListNumbered, mdiFormatColumns,
  mdiFormatAlignJustify, mdiFormatColorHighlight, mdiTablePlus
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
        mdiFormatListNumbered,
        mdiFormatColumns,
        mdiFormatAlignJustify,
        mdiFormatColorHighlight,
        mdiTablePlus
      }
    }
  }
}
</script>
