<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-chip-group
          v-model="selectedThemes"
          column
          multiple
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
      <v-col v-for="(source, i) in sources" :key="source.name" cols="4">
        <v-card flat color="g100">
          <v-card-title>
            {{ source.name }}
          </v-card-title>
          <v-row v-if="source.subTheme">
            <v-col cols="10">
              <v-chip
                outlined
                class="text-capitalize"
                color="bf300 ml-4"
              >
                {{ source.subTheme }}
              </v-chip>
            </v-col>
            <v-col cols="2">
              <v-btn
                :href="i ? `https://www.data.gouv.fr/en/datasets/?q=${source.name}` : 'https://www.datara.gouv.fr/accueil/base_territoriale/'"
                target="_blank"
                icon
              >
                <v-icon small>
                  {{ icons.mdiOpenInNew }}
                </v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { groupBy } from 'lodash'
import { mdiOpenInNew } from '@mdi/js'
import dataSources from '@/assets/data/DataSources.json'

export default {
  data () {
    return {
      dataSources,
      selectedThemes: [],
      icons: {
        mdiOpenInNew
      }
    }
  },
  computed: {
    themes () {
      return groupBy(dataSources, source => source.theme)
    },
    themesKeys () {
      return Object.keys(this.themes).filter(k => k)
    },
    filteredThemes () {
      if (this.selectedThemes.length) {
        const themes = {}

        this.selectedThemes.forEach((themeIndex) => {
          const selectedTheme = this.themesKeys[themeIndex]
          themes[selectedTheme] = this.themes[selectedTheme]
        })

        return themes
      } else {
        return this.themes
      }
    }
  }
}
</script>
