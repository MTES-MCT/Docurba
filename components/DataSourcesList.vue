<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-chip-group
          v-model="selectedTheme"
          column
        >
          <v-chip
            v-for="theme in themes"
            :key="theme.id"
            class="text-capitalize"
            :value="theme.id"
            filter
            outlined
            color="bf500"
          >
            {{ theme.text }}
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
      <v-col v-for="(source, i) in sources" :key="`${theme}-${i}-${source.nom_couche}`" cols="12">
        <v-row>
          <v-col cols="12">
            <h3 class="text-h3">
              {{ source.nom_couche }}
            </h3>
          </v-col>
          <v-col v-for="(obj, j) in source.objets" :key="`${source.nom_couche}-${j}-${obj.nom_couche}`" cols="12" sm="6" md="4">
            <DataSourceCard :sub-theme="source.subTheme" :source="obj" />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { groupBy } from 'lodash'

export default {
  props: {
    dataSources: {
      type: Array,
      default () { return [] }
    },
    themes: {
      type: Array,
      default () { return [] }
    }
  },
  data () {
    return {
      selectedTheme: ''
    }
  },
  computed: {
    filteredThemes () {
      const filterredSources = this.dataSources.filter((source) => {
        return this.selectedTheme ? (source.theme.id === this.selectedTheme) : true
      })

      return groupBy(filterredSources, (source) => {
        return source.theme.text
      })
    }
  }
}
</script>
