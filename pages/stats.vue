<template>
  <v-container class="my-8">
    <StatsProceduresDashboard />
    <StatsNpsDashboard />
    <StatsFdrDashboard />
    <StatsDdtDashboard v-if="diffs" :diffs="diffs" />
    <StatsSocleDashboard />
    <StatsPacDashboard v-if="diffs" :diffs="diffs" />
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      diffs: null
    }
  },
  mounted () {
    this.getPACsDiff()
  },
  methods: {
    async getPACsDiff () {
      const { data: diffs } = await axios({
        url: '/api/stats/diff',
        method: 'get'
      })

      this.diffs = diffs
    }
  }
}
</script>

<style scoped>
.card-loader {
  min-height: 200px;
}

.big-number {
  font-size: 64px;
}
</style>

<style>
.stats-card {
  border: 1px solid #E3E3FD;
  border-color: #E3E3FD !important;
}
</style>
