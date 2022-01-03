<template>
  <v-row>
    <v-col
      v-for="ressource in filteredRessources"
      :key="ressource.title"
      cols="12"
      md="4"
    >
      <v-card
        flat
        color="g100"
        :href="getSource(ressource)"
        target="_blank"
      >
        <v-card-title class="break-word">
          {{ ressource.title }}
        </v-card-title>
        <v-row v-if="ressource.body.children.length">
          <v-col cols="12">
            <v-card-text>
              <nuxt-content :document="ressource" />
            </v-card-text>
          </v-col>
        </v-row>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
export default {
  props: {
    ressources: {
      type: Array,
      required: true
    }
  },
  computed: {
    filteredRessources () {
      return this.ressources.filter((r) => {
        return this.getSource(r)
      })
    },
    selectedRegion () {
      return this.$route.query.region || this.$route.query.r
    }
  },
  methods: {
    getSource (ressource) {
      if (ressource.regions) {
        const region = ressource.regions.find(s => s.iso === this.selectedRegion)

        return region ? region.source : ressource.sourceNational
      } else { return ressource.sourceNational }
    }
  }
}
</script>
