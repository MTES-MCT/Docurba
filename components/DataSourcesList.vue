<template>
  <VGlobalLoader v-if="loading" />
  <v-container v-else-if="dataSources.length">
    <v-row>
      <v-col cols="12">
        <v-chip-group
          v-model="selectedTheme"
          column
        >
          <v-chip
            v-for="theme in displayedThemes"
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
            <DataSourceCard
              :selected="isSelected(obj)"
              :sub-theme="source.subTheme"
              :source="obj.card"
              :region="region"
              :selectable="selectable"
              load-on-active
              @input="changeSelection(obj, $event)"
            />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
  <v-container v-else class="fill-height">
    <v-row class="fill-height" justify="center" align="center">
      <v-col cols="auto">
        <h2 class="text-h2 text-center">
          Aucune donnée n'est disponible pour le moment.
        </h2>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { groupBy } from 'lodash'

export default {
  props: {
    collectivitesCodes: {
      type: Array,
      required: true
    },
    region: {
      type: String,
      default () { return this.$route.query.region }
    },
    selectable: {
      type: Boolean,
      default: false
    },
    selection: {
      type: Array,
      // This should be an array of cardData url created using $daturba
      default () { return [] }
    }
  },
  data () {
    return {
      dataSources: [],
      themes: [],
      selectedTheme: '',
      loading: true
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
    },
    displayedThemes () {
      return this.themes.filter((t) => {
        return !!this.dataSources.find(s => s.theme.id === t.id)
      })
    }
  },
  watch: {
    selectedTheme () {
      // Start Analytics
      if (this.selectedTheme) {
        const theme = this.themes.find(t => t.id === this.selectedTheme).text
        this.$matomo(['trackEvent', 'Data Source', 'Theme', theme])
      }
      // End Analytics
    }
  },
  async created () {
    const { dataset, themes } = await this.$daturba.getData(this.region, this.collectivitesCodes)
    this.dataSources = dataset
    this.themes = themes
    this.loading = false
  },
  methods: {
    changeSelection (sourceObj, selected) {
      if (selected) {
        this.$emit('add', {
          title: sourceObj.nom,
          category: sourceObj.nom_couche,
          source: 'BASE_TERRITORIALE',
          url: sourceObj.carto_url,
          links: sourceObj.ressources.map((r) => {
            return {
              label: r.alias ?? r[0].alias,
              url: r.valeur ?? r[0].valeur
            }
          }),
          extra: {
            id: sourceObj.id,
            table: sourceObj.nom_table
          }
        })
      } else {
        this.$emit('remove', sourceObj.carto_url)
      }
    },
    isSelected (sourceObj) {
      return !!this.selection.find(s => s.url === sourceObj.carto_url)
    }
  }
}
</script>
