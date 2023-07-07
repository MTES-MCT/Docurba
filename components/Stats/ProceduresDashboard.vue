<template>
  <v-row justify="center">
    <v-col cols="12">
      <h2 class="text-h2">
        Nombre de procédures de document d’urbanisme guidées par Docurba
      </h2>
      <!-- <p>
        Indicateur clé d’accompagnement des collectivités dans l’élaboration de leur document d’urbanisme. Il est calculé via la somme des feuilles de route initiées et des projets de PAC en cours.
      </p> -->
    </v-col>
    <v-col cols="12" md="4">
      <StatsTextCard text="Indicateur clé d’accompagnement des collectivités dans l’élaboration de leur document d’urbanisme. Il est calculé via la somme des feuilles de route initiées et des projets de PAC en cours." />
    </v-col>
    <v-col cols="12" lg="8">
      <!-- <StatsSparklineCard title="Nombre de procedures par mois" :points="monthPoints" /> -->
      <StatsBarsCard title="Nombre de procedures par mois" :points="monthPoints" />
    </v-col>
    <v-col cols="12" md="4" lg="4">
      <StatsBignumberCard title="Total de procédures guidées par Docurba" :number="stats.nbProjects" />
    </v-col>
    <v-col v-if="stats.byDept" cols="12" md="8" lg="8">
      <StatsDeptsMapCard title="Repartition des procedures" :points="stats.byDept" />
    </v-col>
  </v-row>
</template>

<script>
import axios from 'axios'
// import departements from '@/assets/data/departements-france.json'

export default {
  data () {
    return {
      stats: {}
    }
  },
  computed: {
    monthPoints () {
      if (this.stats.byMonth) {
        const months = Object.keys(this.stats.byMonth).sort((d1, d2) => {
          return this.$dayjs(d1, 'MM/YY') - this.$dayjs(d2, 'MM/YY')
        }).map((month, index) => {
          return {
            y: this.stats.byMonth[month],
            x: index,
            xLabel: month,
            yLabel: this.stats.byMonth[month]
          }
        })

        // console.log(JSON.stringify(months))

        return months.slice(months.length - 12)
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

      // console.log('Projects Data', data)

      // const ARA = departements.filter((dept) => {
      //   return dept.code_region === 84
      // })

      // const ARAprojects = { total: 0 }

      // ARA.forEach((dept) => {
      //   const nbProjects = data.byDept[dept.code_departement]

      //   ARAprojects[dept.nom_departement] = nbProjects
      //   ARAprojects.total += nbProjects
      // })

      // console.log(JSON.stringify(ARAprojects, null, 2))

      this.stats = data
    }
  }
}
</script>
