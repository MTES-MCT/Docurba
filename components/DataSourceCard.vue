<template>
  <v-lazy v-model="isActive" :min-height="228">
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
        <v-row v-if="filteredChamps.length" dense>
          <v-col v-for="(champ, i) in filteredChamps" :key="`${i}-${champ.alias}`" cols="12">
            <a v-if="champ.type === 'url'" :href="champ.valeur" target="_blank">{{ champ.alias || champ.nom }}</a>
            <span v-else><b>{{ champ.alias || champ.nom }}:</b> {{ champ.valeur }}</span>
          </v-col>
        </v-row>
        <v-row class="py-4">
          <v-col v-for="(ressource, i) in source.ressources" :key="i" cols="12" class="py-0">
            <v-btn
              depressed
              tile
              text
              color="primary"
              :href="ressource.valeur"
              target="_blank"
            >
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
            <v-btn
              depressed
              tile
              block
              color="primary"
              v-on="on"
              @click="showMap"
            >
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
  </v-lazy>
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
    },
    region: {
      type: String,
      default () { return this.$route.query.region }
    }
  },
  data () {
    // console.log(this.source)

    return {
      icons: {
        mdiOpenInNew,
        mdiMap
      },
      iframeLoading: true,
      isActive: false,
      champs: []
    }
  },
  computed: {
    filteredChamps () {
      if (this.champs) {
        return this.champs.filter((c) => {
          // console.log(c, c.valeur, c.url)
          // if (c.type === 'url') { console.log(c) }

          // eslint-disable-next-line eqeqeq
          return c.valeur == 0 || !!c.valeur
        })
      } else { return [] }
    }
  },
  watch: {
    // This can be used to fetch more data when element is visible only.
    async isActive () {
      if (this.isActive) {
        const { champs } = await this.$daturba.getCardData(this.region, this.source)
        this.champs = champs
      }
    }
  },
  methods: {
    showMap () {
      // Start Analytics
      this.$matomo([
        'trackEvent', 'Data Source', 'Carte',
        this.source.nom
      ])
      // End Analytics
    }
  }
}
</script>
