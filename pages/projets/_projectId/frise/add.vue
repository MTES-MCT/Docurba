<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-btn text exact-path color="primary" nuxt :to="`/projets/${projectId}/frise`">
          <v-icon>{{ icons.mdiChevronLeft }}</v-icon> Revenir à la frise
        </v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          Ajouter un événement
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
