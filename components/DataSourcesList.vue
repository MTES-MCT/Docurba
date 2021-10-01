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
      <v-col v-for="(source) in sources" :key="source.title" cols="4">
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
          <v-card-actions v-if="source.sourceNational">
            <v-row justify="end">
              <v-col cols="auto">
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
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { groupBy } from 'lodash'
import { mdiOpenInNew } from '@mdi/js'
// import dataSources from '@/assets/data/DataSources.json'

export default {
  data () {
    return {
      dataSources: [],
      selectedTheme: '',
      icons: {
        mdiOpenInNew
      }
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
      // console.log('themes', this.themes, this.themesKeys)

      if (this.selectedTheme) {
        const theme = {}
        const selectedKey = this.themesKeys[this.selectedTheme]

        theme[selectedKey] = this.themes[selectedKey]

        return theme
      } else {
        return this.themes
      }
    }
  }
}
</script>
