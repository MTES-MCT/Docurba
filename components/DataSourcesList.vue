<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-chip-group
          v-model="selectedTheme"
          column
        >
          <v-chip
            v-for="themeKey in themesKeys"
            :key="themeKey"
            class="text-capitalize"
            filter
            outlined
            color="bf500"
          >
            {{ themeKey }}
          </v-chip>
        </v-chip-group>
      </v-col>
    </v-row>
    <v-row v-for="(sources, theme) in filteredThemes" :key="theme">
      <v-col cols="12">
        <h2 class="text-h2">
          {{ theme }}
        </h2>
      </v-col>
      <v-col v-for="(source) in sources" :key="`${theme}-${source.title}`" cols="12" sm="6" md="4">
        <DataSourceCard :source="source" :region="region" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { groupBy } from 'lodash'

export default {
  props: {
    region: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      dataSources: [],
      selectedTheme: ''
    }
  },
  async fetch () {
    this.dataSources = await this.$content('Data', {
      deep: true
    }).fetch()
  },
  computed: {
    themes () {
      return groupBy(this.dataSources, source => source.theme)
    },
    themesKeys () {
      return Object.keys(this.themes).filter(k => k)
    },
    filteredThemes () {
      const selectedKey = this.themesKeys[this.selectedTheme]

      if (selectedKey) {
        const theme = {}

        theme[selectedKey] = this.themes[selectedKey]

        return theme
      } else {
        return this.themes
      }
    }
  }
}
</script>
