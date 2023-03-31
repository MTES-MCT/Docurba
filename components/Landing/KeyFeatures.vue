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
        floatingTitle: 'CENTRAL & DIRECT',
        title: 'Ressources centralisées et disponibles à tout moment.',
        text: 'Des données territorialisées utiles pour vos documents d\'urbanisme, téléchargeables aux formats .csv ou .shp Ainsi que les premiers éléments  du PAC à échelle nationale et régionale, consultables en ligne immédiatement et mis à jour régulièrement.'
      }, {
        floatingTitle: 'COLLABORATIF & INTERACTIF',
        title: 'Outil rassemblant services de l\'Etat, collectivités et bureaux d\'études',
        text: 'Une feuille de route partagée facilitant la collaboration avec les services de l\'État. Outil destiné au suivi des étapes clef de la procédure et au partage de fichiers lié à celle-ci. La feuille de route vous guide tout au long de votre procédure'
      }, {
        floatingTitle: 'OUTIL DU SERVICE PUBLIC',
        title: 'Conçu avec les services de l’État et le Ministère de la Transition Écologique et de la Cohésion des Territoires.',
        text: 'Outil pensé avec et pour les collectivités, les bureaux d\'études et les services de l\'État pour proposer les informations de références sur les procédures, les dernières lois et décrets d\'application, et les étapes essentielles d\'un document d\'urbanisme.'
      }]
    }
  }
}
</script>
