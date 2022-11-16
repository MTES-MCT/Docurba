<template>
  <v-timeline>
    <v-timeline-item>
      <v-btn nuxt color="primary" :to="`/projets/${projectId}/frise/add`">
        Ajouter un événement
      </v-btn>
    </v-timeline-item>
    <v-timeline-item v-for="e in events" :key="e" right>
      <template #opposite>
        TEST
      </template>
      <v-card outlined>
        <v-card-title>Event</v-card-title>
      </v-card>
    </v-timeline-item>
  </v-timeline>
</template>

<script>
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
      events: [1, 2, 3]
    }
  }
}
</script>
