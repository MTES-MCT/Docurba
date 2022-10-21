<template>
  <v-row justify="space-around" class="py-5" align="center">
    <v-col cols="12" sm="6" md="3" class="collapse-transition">
      <v-row justify="center">
        <v-col cols="10">
          <v-img height="150px" contain :src="require('@/assets/picto/undraw_search.svg')" />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <h4 class="text-body-1 pb-2">
            <b>Je trouve ma trame de pac</b>
          </h4>
          <p class="text-caption">
            En précisant mon territoire et le type de document d’urbanisme.
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
            <b>J'accède aux premiers éléments</b>
          </h4>
          <p class="text-caption">
            Fournis par les services de l’État pour mon département.
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
            <b>Je créer mon compte</b>
          </h4>
          <p class="text-caption">
            Et demande mon PAC à ma Direction Départementale des Territoires (DDT).
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
            <b>Je reçois mon PAC en ligne</b>
          </h4>
          <p class="text-caption">
            Ainsi que ma note d’enjeu, le cas échéant et un accompagnement du projet
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
