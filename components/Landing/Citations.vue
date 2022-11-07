<template>
  <v-container class="mt-10">
    <v-row justify="center">
      <v-col v-for="(c, i) in citations" :key="`citation-${i}`" cols="12" :sm="c.cols">
        <v-card flat class="citation-card pl-2">
          <v-card-title class="break-word">
            <v-divider vertical />
            <v-row no-gutters>
              <v-col cols="12">
                <v-img height="26px" width="26px" :src="require('@/assets/images/icons/verbatisme.svg')" />
              </v-col>
              <v-col>
                <b>« {{ c.text }} »</b>
              </v-col>
            </v-row>
          </v-card-title>
          <v-card-subtitle class="mt-3">
            <v-divider vertical />
            {{ c.author }}
          </v-card-subtitle>
        </v-card>
      </v-col>
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
          author: 'Élus d’une commune de 500 hab',
          cols: 6
        },
        {
          text: 'C’est une plateforme de ressources, qui permet de plus me poser de question sur les éléments à prendre en compte, pour des élus qui n’ont pas toujours ni la connaissance ni la sensibilité elle est facile à comprendre',
          author: 'Élus d’une commune de 700 hab',
          cols: 6
        },
        {
          text: 'C’est une plateforme qui permet d’avoir un peu plus de transparence sur les attendus pour ne pas avoir de points de blocage quand on est plus avancé dans le projet.',
          author: 'Bureau d’étude',
          cols: 6
        },
        {
          text: 'C’est bien que tout soit centralisé, c’est rassurant',
          author: 'Bureau d’étude',
          cols: 3
        },
        {
          text: 'Ca fait gagner du temps.',
          author: 'Bureau d’étude',
          cols: 3
        }
      ]
    }
  }
}
</script>

<style scoped>
.citation-card {
  border-left: thin solid rgba(0,0,0,.12);
}
</style>
