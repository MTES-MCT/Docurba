<template>
  <v-row>
    <v-col cols="2" class="position-relative">
      <!-- DECORAtION GOES HERE -->
      <VFloatingShape src="/images/landing/ellipse_half_blue_left.svg" :size="60" :left="15" :top="-45" />

      <VFloatingShape src="/images/landing/line_left.svg" :width="30" :height="50" :right="1" :top="30" />
      <VFloatingShape src="/images/landing/undraw_completed_tasks.svg" :size="100" :right="30" :top="0" />

      <VFloatingShape src="/images/landing/circle_light_grey.svg" :size="56" :right="50" :top="250" />

      <VFloatingShape src="/images/landing/ellipse_yellow.svg" :size="123" :left="25" :bottom="250" />
      <VFloatingShape src="/images/landing/undraw_completed_tasks.svg" :size="100" :left="50" :bottom="230" />
      <VFloatingShape src="/images/landing/line_left_2.svg" :width="280" :height="200" :right="-10" :bottom="100" />
    </v-col>
    <v-col cols="8">
      <v-row>
        <v-col v-for="(feature, i) in keyFeatures" :key="i" cols="12" class="mb-6">
          <LandingKeyFeatureCard v-bind="feature" />
        </v-col>
      </v-row>
    </v-col>
    <v-col cols="2" class="position-relative">
      <!-- DECORATION GOES HERE -->
      <VFloatingShape src="/images/landing/line_right_1.svg" :width="140" :height="150" :left="-20" :top="50" />
      <VFloatingShape src="/images/landing/undraw_completed_tasks.svg" :size="100" :left="50" :top="200" />
      <VFloatingShape src="/images/landing/line_right_2.svg" :width="240" :height="200" :left="-20" :top="300" />

      <VFloatingShape src="/images/landing/circle_light_red.svg" :size="56" :left="-30" :top="360" />
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
