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
    <v-row>
      <v-col v-for="(card, i) in filterredCards" :key="`${card.title}-${i}`" cols="12" sm="6" md="4">
        <DataSourceCard
          :source="card"
          :region="region"
        />
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
      return this.cards
    }
  }
}
</script>
