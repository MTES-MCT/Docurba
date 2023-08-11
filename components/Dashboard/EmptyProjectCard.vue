<template>
  <v-card outlined>
    <v-card-text>
      <v-row>
        <v-col cols="12" class="text-subtitle-1 font-weight-bold">
          <span>{{ project.doc_type }}</span>
          <br>
          <span>{{ project.name }}</span>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          Aucune procédure existante pour ce {{ project.doc_type }}.
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-btn color="primary" tile disabled>
        Ajouter une procedure
      </v-btn>
      <v-btn color="primary" tile depressed nuxt :to="`/trames/projet-${project.id}`">
        Modifier le PAC
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
<script>
export default {
  props: {
    project: {
      type: Object,
      required: true
    }
  }
}
</script>
