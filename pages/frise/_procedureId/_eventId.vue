<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-btn text exact-path color="primary" nuxt :to="{name: 'ddt-departement-collectivites-collectiviteId-frise-procedureId', params: {departement: $route.params.departement ,collectiviteId: $route.params.collectiviteId, procedureId: $route.params.procedureId}, query: $route.query}">
          <v-icon>{{ icons.mdiChevronLeft }}</v-icon> Revenir à la frise
        </v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          Modification d'évènement
        </h1>
      </v-col>
      <FriseEventForm />
    </v-row>
  </v-container>
</template>

<script>
import { mdiChevronLeft } from '@mdi/js'

export default {
  props: {
    projectId: {
      type: String,
      default () {
        return this.$route.params.projectId
      }
    }
  },
  data () {
    return {
      icons: {
        mdiChevronLeft
      }
    }
  }
}
</script>
