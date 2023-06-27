<template>
  <v-row>
    <v-col cols="12">
      <h2 class="text-h2">
        Zoom sur la feuille de route
      </h2>
      <!-- <p>Indicateur sur les collectivités guidées grâce aux évènements recommandés dans la feuille de route partagée avec le bureau d’études et la DDT/DEAL. Nouvelle fonctionnalité depuis avril 2023. </p> -->
    </v-col>
    <v-col cols="12" md="6">
      <StatsTextCard
        :text="`Indicateur sur les collectivités guidées grâce aux évènements recommandés dans la feuille de route partagée avec le bureau d’études et la DDT/DEAL. Nouvelle fonctionnalité depuis avril 2023.`"
      />
    </v-col>
    <v-col cols="12" md="4">
      <StatsBignumberCard title="Nombre d’évènements ajoutés" :number="stats.nbEvents" />
    </v-col>
  </v-row>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      stats: {}
    }
  },
  mounted () {
    this.getFDR()
  },
  methods: {
    async getFDR () {
      const { data: fdr } = await axios({
        url: '/api/stats/fdr',
        method: 'get'
      })

      this.stats = fdr
    }
  }
}
</script>
