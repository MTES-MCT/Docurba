<template>
  <v-container>
    <v-row justify="center">
      <v-col
        v-for="letter in alphabet"
        :key="letter"
        cols="auto"
      >
        <v-btn
          depressed
          tile
          elevation="2"
          icon
          :disabled="!groupedWords[letter]"
          @click="scrollTo(`${letter}-anchor`)"
        >
          <b>{{ letter }}</b>
        </v-btn>
      </v-col>
    </v-row>
    <v-row v-for="(group) in sortedGroups" :key="group.letter">
      <v-col cols="12">
        <h2 :id="`${group.letter}-anchor`" class="text-h2">
          {{ group.letter }}
        </h2>
      </v-col>
      <v-col v-for="word in group.words" :key="word.titre" cols="12" sm="6" md="4">
        <v-card
          :id="word.titre"
          :ripple="false"
          outlined
        >
          <v-card-title class="break-word">
            {{ word.titre }}
          </v-card-title>
          <v-col cols="12">
            <v-card-text>
              <nuxt-content :document="word" />
            </v-card-text>
          </v-col>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
import { groupBy } from 'lodash'

export default {
  data () {
    return {
      alphabet: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
      wordsData: []
    }
  },
  async fetch () {
    this.wordsData = await this.$content('Glossaire-et-acronymes', {
      deep: true
    }).fetch()
  },
  computed: {
    groupedWords () {
      return groupBy(this.wordsData.filter((word) => {
        return word.titre
      }), (word) => {
        return word.titre[0]
      })
    },
    sortedGroups () {
      return Object.keys(this.groupedWords).sort().map((letter) => {
        return {
          letter,
          words: this.groupedWords[letter]
        }
      })
    }
  },
  methods: {
    scrollTo (targetId) {
      this.$vuetify.goTo(`#${targetId}`)
    }
  }
}
</script>
