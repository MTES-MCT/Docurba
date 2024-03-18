<template>
  <v-toolbar-items>
    <v-tooltip bottom>
      <template #activator="{ on, attrs }">
        <v-btn
          depressed
          tile
          icon
          v-bind="attrs"
          :disabled="!editor.can().deleteTable()"
          v-on="on"
          @click="editor.chain().focus().deleteTable().run()"
        >
          <v-icon>{{ icons.mdiTableRemove }}</v-icon>
        </v-btn>
      </template>
      Supprimer le tableau
    </v-tooltip>

    <v-tooltip bottom>
      <template #activator="{ on, attrs }">
        <v-btn
          depressed
          tile
          icon
          v-bind="attrs"
          :disabled="!editor.can().toggleHeaderColumn()"
          v-on="on"
          @click="editor.chain().focus().toggleHeaderColumn().run()"
        >
          <v-icon>{{ icons.mdiDockLeft }}</v-icon>
        </v-btn>
      </template>
      Activer colonne d'en-tête
    </v-tooltip>

    <v-tooltip bottom>
      <template #activator="{ on, attrs }">
        <v-btn
          depressed
          tile
          icon
          v-bind="attrs"
          :disabled="!editor.can().toggleHeaderRow()"
          v-on="on"
          @click="editor.chain().focus().toggleHeaderRow().run()"
        >
          <v-icon>{{ icons.mdiDockLeft }}</v-icon>
        </v-btn>
      </template>
      Activer ligne d'en-tête
    </v-tooltip>

    <v-tooltip bottom>
      <template #activator="{ on, attrs }">
        <v-btn
          depressed
          tile
          icon
          v-bind="attrs"
          :disabled="!editor.can().addColumnBefore()"
          v-on="on"
          @click="editor.chain().focus().addColumnBefore().run()"
        >
          <v-icon>{{ icons.mdiTableColumnPlusBefore }}</v-icon>
        </v-btn>
      </template>
      Ajouter une colonne avant
    </v-tooltip>

    <v-tooltip bottom>
      <template #activator="{ on, attrs }">
        <v-btn
          depressed
          tile
          icon
          v-bind="attrs"
          :disabled="!editor.can().addColumnAfter()"
          v-on="on"
          @click="editor.chain().focus().addColumnAfter().run()"
        >
          <v-icon>{{ icons.mdiTableColumnPlusAfter }}</v-icon>
        </v-btn>
      </template>
      Ajouter une colonne après
    </v-tooltip>

    <v-tooltip bottom>
      <template #activator="{ on, attrs }">
        <v-btn
          depressed
          tile
          icon
          v-bind="attrs"
          :disabled="!editor.can().deleteColumn()"
          v-on="on"
          @click="editor.chain().focus().deleteColumn().run()"
        >
          <v-icon>{{ icons.mdiTableColumnRemove }}</v-icon>
        </v-btn>
      </template>
      Supprimer la colonne
    </v-tooltip>

    <v-tooltip bottom>
      <template #activator="{ on, attrs }">
        <v-btn
          depressed
          tile
          icon
          v-bind="attrs"
          :disabled="!editor.can().addRowBefore()"
          v-on="on"
          @click="editor.chain().focus().addRowBefore().run()"
        >
          <v-icon>{{ icons.mdiTableRowPlusBefore }}</v-icon>
        </v-btn>
      </template>
      Ajouter une ligne avant
    </v-tooltip>

    <v-tooltip bottom>
      <template #activator="{ on, attrs }">
        <v-btn
          depressed
          tile
          icon
          v-bind="attrs"
          :disabled="!editor.can().addRowAfter()"
          v-on="on"
          @click="editor.chain().focus().addRowAfter().run()"
        >
          <v-icon>{{ icons.mdiTableRowPlusAfter }}</v-icon>
        </v-btn>
      </template>
      Ajouter une ligne après
    </v-tooltip>

    <v-tooltip bottom>
      <template #activator="{ on, attrs }">
        <v-btn
          depressed
          tile
          icon
          v-bind="attrs"
          :disabled="!editor.can().deleteRow()"
          v-on="on"
          @click="editor.chain().focus().deleteRow().run()"
        >
          <v-icon>{{ icons.mdiTableRowRemove }}</v-icon>
        </v-btn>
      </template>
      Supprimer la ligne
    </v-tooltip>

    <v-tooltip bottom>
      <template #activator="{ on, attrs }">
        <v-btn
          depressed
          tile
          icon
          v-bind="attrs"
          :disabled="!editor.can().mergeOrSplit()"
          v-on="on"
          @click="editor.chain().focus().mergeOrSplit().run()"
        >
          <v-icon>{{ icons.mdiTableSplitCell }}</v-icon>
        </v-btn>
      </template>
      Fusionner / Séparer les cellules
    </v-tooltip>
  </v-toolbar-items>
</template>

<script>
import {
  mdiTableColumnPlusBefore, mdiTableColumnPlusAfter, mdiTableColumnRemove,
  mdiTableRowPlusBefore, mdiTableRowPlusAfter, mdiTableRowRemove,
  mdiTableRemove, mdiTableSplitCell, mdiDockLeft, mdiDockTop
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
        mdiTableColumnPlusBefore,
        mdiTableColumnPlusAfter,
        mdiTableColumnRemove,
        mdiTableRowPlusBefore,
        mdiTableRowPlusAfter,
        mdiTableRowRemove,
        mdiTableRemove,
        mdiTableSplitCell,
        mdiDockLeft,
        mdiDockTop
      }
    }
  }
}
</script>
