<template>
  <v-container>
    <v-row>
      <v-col
        v-for="ressource in ressources"
        :key="ressource.title"
        cols="12"
        md="4"
      >
        <v-card
          flat
          color="g100"
          :href="ressource.link"
          target="_blank"
        >
          <v-card-title>
            {{ ressource.title }}
          </v-card-title>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  data () {
    return {
      ressources: [{
        title: 'Centre de ressource régional des paysages',
        link: 'http://www.paysages.auvergne-rhone-alpes.gouv.fr/'
      }, {
        title: 'Site du Cerema sur les outils de l‘aménagement',
        link: 'http://outil2amenagement.cerema.fr/'
      }, {
        title: 'Guide de référence pour l‘évaluation environnementale des documents d‘urbanisme',
        link: 'https://www.ecologie.gouv.fr/sites/default/files/Th%C3%A9ma%20-%20Guide%20de%20l%E2%80%99%C3%A9valuation%20environnementale%20des%20documents%20d%E2%80%99urbanisme.pdf'
      }, {
        title: 'Guide de la modernisation du contenu du plan local d‘urbanisme',
        link: 'http://outil2amenagement.cerema.fr/IMG/pdf/guide_de_la_modernisation_du_contenu_du_plan_local_d_urbanisme_-_avril_2017_cle2a4cd4.pdf'
      }, {
        title: 'Dossier de presse sur la loi Climat et Résilience ',
        link: 'https://www.ecologie.gouv.fr/sites/default/files/2021.08.24-DP_Loi_climat_promulguee.pdf'
      }]
    }
  }
}
</script>
