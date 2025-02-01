<template>
  <v-row>
    <v-col cols="12">
      <h2 class="text-h2">
        Net Promoter Score
      </h2>
      <!-- <p>Le Net Promoter Score (NPS) est un outil de satisfaction qui mesure la tendance qu’ont les utilisateurs à recommander un produit à leurs collègues. Le score s'étend de -100 à +100. Un "bon NPS" est un résultat supérieur à 30 ; les utilisateurs sont alors considérés comme satisfaits et sont les promoteurs du produit. Plus d’informations sur le barème : <a href="https://feedier.com/fr/blog/bon-nps-net-promoter-score" target="_blank">net promoter score/</a></p> -->
    </v-col>
    <v-col cols="12" md="4">
      <StatsBignumberCard title="Net Promoter Score" number="50" />
    </v-col>
    <v-col cols="12" md="6">
      <StatsTextCard
        :text="`Le Net Promoter Score (NPS) est un outil de satisfaction qui mesure la tendance qu’ont les utilisateurs à recommander un produit à leurs collègues. Le score s'étend de -100 à +100. Un bon NPS est un résultat supérieur à 30 ; les utilisateurs sont alors considérés comme satisfaits et sont les promoteurs du produit.`"
        :action="{text: 'Plus d’informations sur le barème', link: 'https://feedier.com/fr/blog/bon-nps-net-promoter-score'}"
      />
    </v-col>
    <!-- <v-col cols="12" md="6">
      <StatsBignumberCard title="NPS des collectivités" number="7,6" />
    </v-col> -->
  </v-row>
</template>
