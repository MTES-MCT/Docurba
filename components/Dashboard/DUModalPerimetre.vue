<template>
  <v-dialog
    v-model="dialog"
    width="900"
  >
    <template #activator="{ on, attrs }">
      <span
        v-bind="attrs"
        class="primary--text text-decoration-underline mr-4"
        v-on="on"
      >
        Liste des communes concernées ({{ towns.length }})
      </span>
    </template>

    <v-card>
      <v-card-title class="text-h5 primary white--text">
        Liste des communes concernées ({{ towns.length }})
      </v-card-title>

      <v-card-text class="pb-0">
        <v-container class="py-8">
          <v-row>
            <v-col
              v-for="town in sortedTowns"
              :key="town.inseeCode"
              cols="4"
              class="pl-0"
            >
              <nuxt-link :to="{ name: 'ddt-departement-collectivites-collectiviteId-commune', params: { departement: $route.params.departement, collectiviteId: town.inseeCode }, query: { isEpci: false } }">
                {{ town.name }} ({{ town.inseeCode }})
              </nuxt-link>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-spacer />
        <v-btn
          color="primary"
          text
          @click="dialog = false"
        >
          Fermer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    towns: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      dialog: false
    }
  },
  computed: {
    sortedTowns () {
      return [...this.towns].sort((a, b) => a.name.localeCompare(b.name))
    }
  }
}
</script>
