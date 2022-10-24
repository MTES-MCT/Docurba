<template>
  <v-row>
    <v-col cols="2">
      <!-- DECORAtION GOES HERE -->
    </v-col>
    <v-col cols="8">
      <v-row>
        <v-col v-for="(feature, i) in keyFeatures" :key="i" cols="12" class="mb-6">
          <LandingKeyFeatureCard v-bind="feature" />
        </v-col>
      </v-row>
    </v-col>
    <v-col cols="2">
      <!-- DECORATION GOES HERE -->
    </v-col>
  </v-row>
</template>
<script>
export default {
  data () {
    return {
      keyFeatures: [{
        floatingTitle: 'DIRECT',
        title: 'Ressources disponibles immédiatement.',
        text: 'Les éléments nationaux et régionaux, ainsi que les données concernant votre territoire sont mis à votre disposition par les services de l’Etat et téléchargeables aux formats .csv ou .shp.'
      }, {
        floatingTitle: 'LISIBLE',
        title: 'Navigation optimisée dans votre porter-à-connaissance.',
        text: 'Les données et informations du PAC sont mises en forme et faciles à consulter grâce à différents niveaux d’informations, et des fonctionnalités de commentaires ou partages au sein de l’équipe.'
      }, {
        floatingTitle: 'COLLABORATIF',
        title: 'Accompagnement des services de l’Etat.',
        text: 'La plateforme propose une FAQ dédiée, et l’option feuille de route partagée avec la possibilité de suivre les étapes clés de la procédure. Vous pouvez ainsi offrir de la visibilité aux Services de l’Etat associées lors de l’élaboration du document d’urbanisme.'
      }, {
        floatingTitle: 'COMPLET',
        title: 'Un maximum d’informations centralisées au même endroit.',
        text: 'Documents supra-territoriaux (SRADDET, SCoT…), les données et le porter à connaissance préparé par la Direction Départementale du Territoire (DDT) en partenariat avec la DGALN (Direction Générale de l’Aménagement, du Logement et du Territoire) en partenariat avec les Directions Régionales de l’Environnement, de l’Aménagement et du Logement (DREAL).'
      }]
    }
  }
}
</script>
