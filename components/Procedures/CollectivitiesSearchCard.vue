<template>
  <v-card flat outlined color="alt-beige">
    <v-card-text>
      <v-row>
        <v-col cols="4">
          <v-text-field dense hide-details filled label="Rechercher">
            <template #append>
              <v-btn icon color="primary">
                <v-icon>{{ icons.mdiMagnify }}</v-icon>
              </v-btn>
            </template>
          </v-text-field>
        </v-col>
        <v-col cols="12">
          <v-divider />
        </v-col>
        <v-col cols="auto">
          <v-select :value="'Toutes collectivité porteuse'" hide-details :items="competencesFilters" />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>
<script>
import { mdiMagnify } from '@mdi/js'

export default {
  props: {
    value: {
      type: Array,
      required: true
    },
    collectivities: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      icons: { mdiMagnify },
      competencesFilters: ['Toutes collectivité porteuse']
    }
  }
}
</script>
