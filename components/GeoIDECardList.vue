<template>
  <v-container v-if="cards.length">
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
    <v-row>
      <v-col
        v-for="(card, i) in filterredCards"
        :key="`${card.title}-${i}`"
        cols="12"
        sm="6"
        md="6"
        lg="6"
        xl="4"
      >
        <DataSourceCard
          :source="card"
          :region="region"
        />
      </v-col>
    </v-row>
  </v-container>
  <v-container v-else class="fill-height">
    <v-row class="fill-height" justify="center" align="center">
      <v-col cols="auto">
        <h2 class="text-h5 text-center">
          Aucune donnée n'est disponible pour le moment.
        </h2>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  props: {
    themes: {
      type: Array,
      required: true
    },
    cards: {
      type: Array,
      required: true
    },
    region: {
      type: String,
      default () { return this.$route.query.region }
    }
  },
  data () {
    return {
      selectedTheme: null
    }
  },
  computed: {
    filterredCards () {
      if (this.selectedTheme) {
        return this.cards.filter((card) => {
          return !!card.categs.find(categ => categ.includes(this.selectedTheme))
        })
      } else { return this.cards }
    }
  }
}
</script>
