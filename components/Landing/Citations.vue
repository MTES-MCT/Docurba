<template>
  <v-container class="mt-10">
    <v-row justify="center">
      <!-- <v-spacer v-if="i%2 === 1" /> -->
      <!-- <v-col v-if="i%2 === 1" cols="7">
        <v-card flat>
          <v-card-title class="d-block text-right">
            {{ c.author }}
          </v-card-title>
        </v-card>
      </v-col> -->
      <v-col v-for="(c, i) in citations" :key="`citation-${i}`" cols="12" sm="6">
        <!-- <v-card flat color="rm300" dark> -->
        <v-card flat>
          <!-- <v-card flat color="bf300" dark> -->
          <v-card-text class="font-italic d-flex">
            <!-- <v-row>
              <v-col cosl="auto"> -->
            <span class="text-h3">“</span>
            <!-- </v-col>
              <v-col cols=""> -->
            <span class="pt-6">{{ c.text }}</span>
            <!-- </v-col>
              <v-col cols="auto"> -->
            <span class="text-h3">”</span>
            <!-- </v-col>
            </v-row> -->
          </v-card-text>
          <v-card-title class="d-block text-right">
            {{ c.author }}
          </v-card-title>
        </v-card>
      </v-col>
      <!-- <v-col cols="6">
        <v-card flat>
          <v-card-title class="d-block text-right">
            {{ c.author }}
          </v-card-title>
        </v-card>
      </v-col> -->
    </v-row>
  </v-container>
</template>

<script>
export default {
  data () {
    return {
      citations: [
        {
          text: 'C’est une plateforme de ressources pour nous guider dans notre démarche de PLU et dans laquelle on va retrouver à la fois des documents de référence, des données qui nous sont utiles pour l’élaboration du document et puis une aide à la conduite du projet',
          author: 'Élus d’une commune de 500 hab'
        },
        {
          text: 'C’est une plateforme de ressources, qui permet de plus me poser de question sur les éléments à prendre en compte, pour des élus qui n’ont pas toujours ni la connaissance ni la sensibilité elle est facile à comprendre',
          author: 'Élus d’une commune de 700 hab'
        },
        {
          text: 'C’est une plateforme qui permet d’avoir un peu plus de transparence sur les attendus pour ne pas avoir de points de blocage quand on est plus avancé dans le projet.',
          author: 'Bureau d’étude'
        },
        {
          text: 'Ca fait gagner du temps',
          author: 'Bureau d’étude'
        },
        {
          text: 'C’est bien que tout soit centralisé, c’est rassurant',
          author: 'Bureau d’étude'
        }
      ]
    }
  }
}
</script>
