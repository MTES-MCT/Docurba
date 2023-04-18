<template>
  <v-container fluid>
    <v-row justify="space-around" class="py-5 mt-10 fill-height" align="stretch">
      <v-col cols="12" sm="6" md="3" class="collapse-transition">
        <div class="pa-4 card-us">
          <h4 class="text-body-1 pb-3">
            <b>Acte</b>
          </h4>
          <div class="text-caption">
            Déposer un acte qui concerne l'élaboration, la révision ou l'évolution de vos documents d'urbanisme
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3" class="collapse-transition">
        <div class="pa-4 card-us">
          <h4 class="text-body-1 pb-3">
            <b>Socle de Porter à Connaissance</b>
          </h4>
          <div class="text-caption">
            Consulter les premiers éléments d'informations disponibles pour votre territoire.
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3" class="collapse-transition">
        <div class="pa-4 card-us">
          <h4 class="text-body-1 pb-3">
            <b>Feuille de route</b>
          </h4>
          <div class="text-caption">
            Suivre vos procédures à l'aide d'un tableau de bord et d'une feuille de route partagée avec les services de l'Etat.
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="3" class="collapse-transition">
        <div class="pa-4 card-us">
          <h4 class="text-body-1 pb-3">
            <b>Données</b>
          </h4>
          <div class="text-caption">
            Accéder à des données territorialisées utiles dans l'élaboration de vos documents d'urbanisme.
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
export default {
  methods: {
    cardSizeClass (isHover) {
      if (isHover) {
        return 'hoveredCard'
      } else if (this.card1 || this.card2 || this.card3 || this.card4) {
        return 'smallCard'
      } else {
        return ''
      }
    }
  }
}
</script>

<style scoped>
.card-us{
  background: #FFFFFF;
  border: 2px solid #F9F8F6;
  border-radius: 8px;
  width: 100%;
  height: 100% !important;
  margin: auto;
}
</style>
