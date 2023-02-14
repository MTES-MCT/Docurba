<template>
  <v-lazy v-model="isActive" :min-height="228">
    <v-card flat outlined>
      <v-card-title class="break-word">
        {{ source.title }}
        <v-btn
          v-if="selectable"
          color="primary"
          dark
          absolute
          top
          right
          fab
          small
          @click="$emit('input', !selected)"
        >
          <v-icon>{{ selected ? icons.mdiCheck : icons.mdiPlus }}</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12">
            <v-chip
              v-for="tag in source.tags"
              :key="tag"
              outlined
              class="text-capitalize"
              color="bf300"
            >
              {{ tag }}
            </v-chip>
          </v-col>
        </v-row>
        <v-row v-if="source.text" class="source-text">
          <v-col>{{ source.text }}</v-col>
        </v-row>
        <v-row v-if="filteredChamps.length" dense>
          <v-col v-for="(champ, i) in filteredChamps" :key="`${i}-${champ.alias}`" cols="12">
            <a v-if="champ.type === 'url'" :href="champ.valeur" target="_blank">{{ champ.alias || champ.nom }}</a>
            <span v-else><b>{{ champ.alias || champ.nom }}:</b> {{ champ.valeur }}</span>
          </v-col>
        </v-row>
        <v-row class="py-4">
          <v-col v-for="(link, i) in source.links" :key="i" cols="12" class="py-0">
            <v-btn
              max-width="100%"
              depressed
              tile
              text
              color="primary"
              :href="link.url"
              target="_blank"
              class="source-link"
            >
              <v-icon small class="mr-2">
                {{ icons.mdiOpenInNew }}
              </v-icon>
              {{ link.text }}
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-dialog v-if="source.mainLinkType === 'iframe'" height="600px" width="900px">
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
            <iframe width="900" height="600" :src="source.mainLink" />
          </v-card>
        </v-dialog>
        <v-btn
          v-else
          depressed
          tile
          block
          color="primary"
          :href="source.mainLink"
          target="_blank"
        >
          Voir la ressource
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-lazy>
</template>

<script>
import { mdiOpenInNew, mdiMap, mdiPlus, mdiCheck } from '@mdi/js'

// import axios from 'axios'

export default {
  model: {
    prop: 'selected',
    event: 'input'
  },
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
    },
    selectable: {
      type: Boolean,
      default: false
    },
    selected: {
      type: Boolean,
      default: false
    },
    loadOnActive: {
      type: Boolean,
      default: false
    }
  },
  data () {
    // console.log(this.source)

    return {
      icons: {
        mdiOpenInNew,
        mdiMap,
        mdiPlus,
        mdiCheck
      },
      iframeLoading: true,
      isActive: false,
      champs: this.source.champs || []
    }
  },
  computed: {
    filteredChamps () {
      if (this.champs) {
        console.log('this.champs: ', this.champs)
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
      if (this.isActive && this.loadOnActive && !this.champs.length) {
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

<style>
.source-text {
  max-height: 200px;
  overflow: scroll;
}

.link-text {
  max-width: 100%;
  display: inline-block;
}

.source-link .v-btn__content {
  max-width: 100%;
  display: block;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}
</style>
