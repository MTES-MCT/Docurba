<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="text-h1">
          Informations générales
        </div>
      </v-col>
      <v-col cols="12">
        <!-- <div class="d-flex">
          <nuxt-link
            :to="{ name: `ddt-departement-collectivites-collectiviteId-${$sudocu.isEpci($route.params.collectiviteId) ? 'epci' : 'commune'}`, params: { departement: $route.params.departement, collectiviteId: $route.params.collectiviteId }}"
          >
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span>Revenir à mon tableau de bord</span>
          </nuxt-link>
        </div> -->
      </v-col>
    </v-row>
    <DashboardDdtInfosTabs />
    <v-row class="white">
      <v-col cols="12">
        <div>
          <div class="text-h2">
            Description
          </div>
          <div class="text-h2">
            Maîtrise d'oeuvre
          </div>
          <div class="text-h2">
            Historique Sudocuh
          </div>
          <div class="text-h2">
            Commentaire/Note
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'InformationsGenerales',
  layout: 'ddt'
}
</script>
