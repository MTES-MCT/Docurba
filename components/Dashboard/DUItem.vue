<template>
  <v-card outlined class="mb-4">
    <v-container>
      <v-row>
        <v-col cols="12" class="text-subtitle-1 font-weight-bold">
          PLUi - Plan Local d’Urbanisme intercommunal
        </v-col>
      </v-row>
      <v-row class="mt-0">
        <v-col cols="1">
          <div class="text-caption g600--text">
            Statut
          </div>
          <div>
            <v-chip>En cours</v-chip>
          </div>
        </v-col>
        <v-col cols="12" class="pb-0">
          <v-divider />
        </v-col>
        <v-col cols="12">
          <span class="primary--text text-decoration-underline mr-4">
            Liste des communes concernées
          </span>
          <span class="primary--text text-decoration-underline mr-4">
            Feuille de route partagée
          </span>
          <span class="primary--text text-decoration-underline mr-4">
            PAC
          </span>
          <span class="primary--text text-decoration-underline">
            Note d'enjeux
          </span>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>
<script>
export default {
  data () {
    return {

    }
  }
}
</script>
