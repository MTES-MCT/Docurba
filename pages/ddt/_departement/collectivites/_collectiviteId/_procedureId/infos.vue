<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="text-h1">
          Informations générales
        </div>
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <!-- <nuxt-link
            :to="{ name: `ddt-departement-collectivites-collectiviteId-${$sudocu.isEpci($route.params.collectiviteId) ? 'epci' : 'commune'}`, params: { departement: $route.params.departement, collectiviteId: $route.params.collectiviteId }}"
          >
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span>Revenir à mon tableau de bord</span>
          </nuxt-link> -->
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-tabs
          background-color="transparent"
        >
          <v-tab :to="{name: 'ddt-departement-collectivites-collectiviteId-procedureId-infos', params: {departement: $route.params.departement ,collectiviteId: $route.params.collectiviteId, procedureId: $route.params.procedureI}}">
            Informations générales
          </v-tab>
          <v-tab :to="{name: 'ddt-departement-collectivites-collectiviteId-procedureId-volet_qualitatif', params: {departement: $route.params.departement ,collectiviteId: $route.params.collectiviteId, procedureId: $route.params.procedureI}}">
            Volet qualitatif
          </v-tab>
          <v-tab :to="{name: 'ddt-departement-collectivites-collectiviteId-procedureId-perimetre', params: {departement: $route.params.departement ,collectiviteId: $route.params.collectiviteId, procedureId: $route.params.procedureId}}">
            Communes concernées
          </v-tab>
        </v-tabs>
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
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'InformationsGenerales',
  layout: 'ddt',
  data () {
    return {

    }
  },
  async mounted () {
    this.collectivite = await this.$sudocu.getCurrentCollectivite(this.$route.params.collectiviteId, 'commune')
  }
}
</script>
