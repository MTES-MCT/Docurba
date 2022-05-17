<template>
  <v-card flat color="g100">
    <v-card-title class="break-word">
      {{ source.nom }}
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col v-if="subTheme" cols="12">
          <v-chip
            outlined
            class="text-capitalize"
            color="bf300"
          >
            {{ subTheme.text }}
          </v-chip>
        </v-col>
      </v-row>
      <v-row class="py-4">
        <v-col v-for="(ressource, i) in source.ressources" :key="i" cols="12" class="py-0">
          <v-btn text color="primary" :href="ressource.valeur" target="_blank">
            <v-icon small class="mr-2">
              {{ icons.mdiOpenInNew }}
            </v-icon>
            {{ ressource.alias }}
          </v-btn>
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-dialog height="600px" width="900px">
        <template #activator="{on}">
          <v-btn block depressed color="primary" v-on="on">
            <v-icon class="pr-2">
              {{ icons.mdiMap }}
            </v-icon>
            Voir la carte
          </v-btn>
        </template>
        <v-card height="600px" width="900px">
          <iframe width="900" height="600" :src="source.carto_url" />
        </v-card>
      </v-dialog>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mdiOpenInNew, mdiMap } from '@mdi/js'

// import axios from 'axios'

export default {
  props: {
    source: {
      type: Object,
      required: true
    },
    subTheme: {
      type: Object,
      default () { return {} }
    }
  },
  data () {
    return {
      icons: {
        mdiOpenInNew,
        mdiMap
      },
      iframeLoading: true
    }
  }
}
</script>
