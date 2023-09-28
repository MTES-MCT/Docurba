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
// import depts from '@/assets/data/departements-france.json'

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

      // console.log(diffs)

      // const ARA = depts.filter((dept) => {
      //   return dept.code_region === 84
      // })

      // const ARAprojects = { total: 0 }

      // ARA.forEach((dept) => {
      //   const nbProjects = diffs[dept.code_departement]

      //   ARAprojects[dept.nom_departement] = nbProjects
      //   ARAprojects.total += nbProjects
      // })

      // console.log(JSON.stringify(ARAprojects, null, 2))
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
