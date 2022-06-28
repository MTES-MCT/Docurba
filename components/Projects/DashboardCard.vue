<template>
  <v-card flat>
    <v-card-title>{{ project.title }}</v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="4">
          <v-card>
            <v-card-subtitle>
              Porté à connaissance
            </v-card-subtitle>
            <v-card-actions>
              <v-btn>Télécharger</v-btn>
              <v-btn>Consulter</v-btn>
              <v-btn>Charger</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col cols="4">
          <v-card>
            <v-card-subtitle>
              Jeux de données
            </v-card-subtitle>
            <v-card-actions>
              <v-btn>Consulter</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col cols="4">
          <v-card>
            <v-card-subtitle>
              Partage
            </v-card-subtitle>
            <v-card-text>
              List de partage
            </v-card-text>
            <v-card-actions>
              <v-btn>Partager</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
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
