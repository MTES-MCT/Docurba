<template>
  <v-menu>
    <template #activoator="{on}">
      <v-badge :content="files.length">
        <v-btn icon v-on="on">
          <v-icon>{{ icons.mdiFile }}</v-icon>
        </v-btn>
      </v-badge>
    </template>
    <v-list>
      <v-list-item
        v-for="(file, fileIndex) in files"
        :key="fileIndex"
        :href="file.url"
        taget="_blank"
      >
        <v-list-item-title>{{ file.name }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>
import { mdiFile } from '@mdi/js'

export default {
  props: {
    files: {
      type: Array,
      default () {
        return []
      }
    }
  },
  data () {
    return {
      icons: { mdiFile }
    }
  }
}
</script>
