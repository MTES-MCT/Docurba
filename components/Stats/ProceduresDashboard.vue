<template>
  <v-row justify="center">
    <v-col cols="12">
      <h2 class="text-h2">
        Nombre de procédures de document d’urbanisme guidées par Docurba
      </h2>
      <p>
        Indicateur clé d’accompagnement des collectivités dans l’élaboration de leur document d’urbanisme. Il est calculé via la somme des feuilles de route initiées et des projets de PAC en cours.
      </p>
    </v-col>
    <v-col cols="12" md="4" lg="4" order="2" order-lg="1">
      <StatsBignumberCard title="Total de procédures guidées par Docurba" :number="stats.nbProjects" />
    </v-col>
    <v-col cols="12" lg="8" order="1" order-lg="2">
      <StatsSparklineCard title="Nombre de procedures par mois" :points="monthPoints" />
    </v-col>
    <v-col v-if="stats.byDept" cols="12" md="8" lg="6" order="3">
      <StatsDeptsMapCard title="Repartition des procedures" :points="stats.byDept" />
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
  computed: {
    monthPoints () {
      if (this.stats.byMonth) {
        return Object.keys(this.stats.byMonth).sort((d1, d2) => {
          return this.$dayjs(d1, 'MM/YY') - this.$dayjs(d2, 'MM/YY')
        }).map((month, index) => {
          return {
            value: this.stats.byMonth[month],
            label: month
          }
        })
      } else {
        return []
      }
    }
  },
  mounted () {
    this.getNbProjects()
  },
  methods: {
    async getNbProjects () {
      const { data } = await axios({
        url: '/api/stats/projects',
        method: 'get'
      })

      // console.log('data', data)

      this.stats = data
    }
  }
}
</script>
