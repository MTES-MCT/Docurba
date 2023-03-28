<template>
  <v-container class="mt-10">
    <v-row>
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
          text: 'Je trouve que c’est une très bonne idée, même avec nos très bonnes relations avec la DDT et nos collectivités, nous n’avons pas d’outils qui nous permettent une telle communication et partage de documents avec les services de l’État',
          author: 'Agence d\'urbanisme',
          cols: 6
        },
        {
          text: 'C’est une plateforme de ressources, qui permet de plus me poser de question sur les éléments à prendre en compte, pour des élus qui n’ont pas toujours ni la connaissance ni la sensibilité elle est facile à comprendre',
          author: 'Élus d’une commune de 700 hab',
          cols: 6
        },
        {
          text: 'La recherche de données est très chronophage pour nous, les voir centralisées sur l’outil nous rassure et nous permet de mutualiser un certain nombre d’engagements, au lieu d\'aller auprès de chaque partenaire.',
          author: 'Intercommunalité (11 communes, 11,000 habitants)',
          cols: 6
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
