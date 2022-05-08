<template>
  <v-container fluid class="px-8">
    <!-- User stories
    <v-row class="py-16">
      <v-col cols="12">
        <h2 class="text-h2">
          Comment ça marche?
        </h2>
      </v-col>
    </v-row> -->
    <v-row justify="space-around" align="center">
      <v-col cols="12" sm="6" md="3" class="collapse-transition" :class="cardSizeClass(card1)">
        <v-hover v-model="card1">
          <v-card flat class="pointer" :height="card1 ? 320 : 320" color="g100">
            <v-row justify="center">
              <v-col cols="10">
                <v-img height="150px" contain :src="require('@/assets/picto/undraw_search.svg')" />
              <!-- <v-sheet height="200" width="200" color="g300" /> -->
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-card-text>
                  <b>Je précise mon territoire</b> et le type de document d’urbanisme
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </v-hover>
      </v-col>
      <v-col cols="12" sm="6" md="3" class="collapse-transition" :class="cardSizeClass(card2)">
        <v-hover v-model="card2">
          <v-card flat class="pointer" :height="card2 ? '' : 320" color="g100">
            <v-row justify="center">
              <v-col cols="10">
                <v-img height="150px" contain :src="require('@/assets/picto/undraw_file_analysis.svg')" />
              <!-- <v-sheet height="200" width="200" color="g300" /> -->
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-card-text>
                  <b>J’accède aux premiers éléments</b> fournis par les Services de l’Etat pour mon département
                </v-card-text>
                <v-card-text v-show="card2">
                  Avec Docurba, le socle de Porter-à-connaissance (PAC) est en libre accès avec les ressources suivantes disponibles pour chaque territoire :
                  <ul>
                    <li>le cadre juridique national</li>
                    <li>les éléments régionaux (SRADDET & doctrine régionale)</li>
                    <li>les données territorialisées</li>
                  </ul>
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </v-hover>
      </v-col>
      <v-col cols="12" sm="6" md="3" class="collapse-transition" :class="cardSizeClass(card3)">
        <v-hover v-model="card3">
          <v-card flat class="pointer" :height="card3 ? '' : 320" color="g100">
            <v-row justify="center">
              <v-col cols="10">
                <v-img height="150px" contain :src="require('@/assets/picto/undraw_profile.svg')" />
              <!-- <v-sheet height="200" width="200" color="g300" /> -->
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-card-text>
                  <b>Je crée un compte</b>
                  et demande mon
                  <LandingPACTooltip /> à ma DDT
                  (Direction Départementale des Territoires)
                </v-card-text>
                <v-card-text v-show="card3" class="collapse-transition">
                  Le <LandingPACTooltip /> contient les informations nécessaires à l’exercice de leurs compétences en matière d’urbanisme notamment le cadre législatif et réglementaire à respecter ou encore les protections existantes en matière d’environnement et de patrimoine sur le territoire.
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </v-hover>
      </v-col>
      <v-col cols="12" sm="6" md="3" class="collapse-transition" :class="cardSizeClass(card4)">
        <v-hover v-model="card4">
          <v-card flat class="pointer" :height="card4 ? 320 : 320" color="g100">
            <v-row justify="center">
              <v-col cols="10">
                <v-img height="150px" contain :src="require('@/assets/picto/undraw_message_sent.svg')" />
              <!-- <v-sheet height="200" width="200" color="g300" /> -->
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-card-text>
                  <b>Je reçois mon <LandingPACTooltip /> en ligne,</b>
                  ma note d’enjeux le cas échéant,
                  et un accompagnement du projet
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </v-hover>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
export default {
  data () {
    return {
      card1: false,
      card2: false,
      card3: false,
      card4: false
    }
  },
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
.hoveredCard {
  flex: 0 0 31% !important;
  max-width: 31% !important;
}

.smallCard {
  flex: 0 0 23% !important;
  max-width: 23% !important;
}

.collapse-transition {
  /* transition: all 300ms; */
}
</style>
