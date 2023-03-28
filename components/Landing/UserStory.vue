<template>
  <v-row justify="space-around" class="py-5 mt-10" align="center">
    <v-col cols="12" sm="6" md="3" class="collapse-transition">
      <v-row justify="center">
        <v-col cols="10">
          <v-img height="150px" contain :src="require('@/assets/picto/undraw_search.svg')" />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <h4 class="text-body-1 pb-2">
            <b>Acte</b>
          </h4>
          <p class="text-caption">
            Consulter un acte qui concerne l'élaboration, la révision ou l'évolution de vos documents d'urbanisme
          </p>
        </v-col>
      </v-row>
    </v-col>
    <v-col cols="12" sm="6" md="3" class="collapse-transition">
      <v-row justify="center">
        <v-col cols="10">
          <v-img height="150px" contain :src="require('@/assets/picto/undraw_file_analysis.svg')" />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <h4 class="text-body-1 pb-2">
            <b>Socle de Porter à Connaissance</b>
          </h4>
          <p class="text-caption">
            Consulter les premiers éléments d'informations disponibles pour votre territoire.
          </p>
        </v-col>
      </v-row>
    </v-col>
    <v-col cols="12" sm="6" md="3" class="collapse-transition">
      <v-row justify="center">
        <v-col cols="10">
          <v-img height="150px" contain :src="require('@/assets/picto/undraw_profile.svg')" />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <h4 class="text-body-1 pb-2">
            <b>Feuille de route</b>
          </h4>
          <p class="text-caption">
            Suivre vos procédures à l'aide d'un tableau de bord et d'une feuille de route partagée avec les services de l'Etat.
          </p>
        </v-col>
      </v-row>
    </v-col>
    <v-col cols="12" sm="6" md="3" class="collapse-transition">
      <v-row justify="center">
        <v-col cols="10">
          <v-img height="150px" contain :src="require('@/assets/picto/undraw_message_sent.svg')" />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <h4 class="text-body-1 pb-2">
            <b>Données</b>
          </h4>
          <p class="text-caption">
            Accéder à des données territorialisées utiles dans l'élaboration de vos documents d'urbanisme.
          </p>
        </v-col>
      </v-row>
    </v-col>
  </v-row>
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
</style>
