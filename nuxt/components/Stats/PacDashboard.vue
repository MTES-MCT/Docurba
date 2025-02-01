<template>
  <v-row>
    <v-col cols="12">
      <h2 class="text-h2">
        Contenu du PAC complet
      </h2>
      <!-- <p>
        Indicateur pour mesurer l’intérêt des DDT à utiliser la trame de PAC pour la mise à jour régulière du cadre juridique national, et la mutualisation d’éléments entre DDT et territoires similaires
      </p> -->
    </v-col>
    <v-col cols="12" md="6">
      <StatsTextCard
        :text="`Indicateurs pour mesurer l’intérêt des DDT à utiliser la trame de PAC pour la mise à jour régulière du cadre juridique national, et la mutualisation d’éléments entre DDT et territoires similaires`"
      />
    </v-col>
    <v-col cols="12" md="4">
      <StatsBignumberCard title="Propositions d’amélioration de contenu de la part des DDT" number="33" />
    </v-col>
    <v-col cols="12" md="5">
      <StatsBignumberCard title="Retours de DDT traités avec QV4" number="13" />
    </v-col>
    <v-col cols="12" md="5">
      <StatsBignumberCard title="Modifications réalisées par les DDT pour paramétrer leur trame départementale " :number="diffs.total" />
    </v-col>
  </v-row>
</template>
<script>
export default {
  props: {
    diffs: {
      type: Object,
      required: true
    }
  }
}
</script>
