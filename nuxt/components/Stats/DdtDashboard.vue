<template>
  <v-row justify="center">
    <v-col cols="12">
      <h2 class="text-h2">
        Utilisation du PAC côté DDT/DEAL
      </h2>
      <!-- <p>
        Indicateur sur les DDT/DEAL Adoptant progressivement l’outil d’édition du PAC pour transmettre plus rapidement le contenu aux collectivités
      </p> -->
    </v-col>
    <v-col cols="12" md="4">
      <v-row>
        <v-col cols="12">
          <StatsBignumberCard title="Nombre d’agents de DDT/DEAL inscrits sur Docurba" :number="stats.nbAdmins" />
        </v-col>
        <v-col cols="12">
          <StatsTextCard
            :text="`Indicateur sur les DDT/DEAL Adoptant progressivement l’outil d’édition du PAC pour transmettre plus rapidement le contenu aux collectivités`"
          />
        </v-col>
      </v-row>
    </v-col>
    <v-col cols="12" md="8">
      <StatsDeptsMapCard
        v-if="mapPoints"
        title="Carte des DDT"
        :points="mapPoints"
        :scale-points="[
          {value: 1, label: 'Démonstration de l’outil'},
          {value: 2, label: 'Création de compte'},
          {value: 3, label: 'Paramétrage de trame'},
          {value: 4, label: 'Réalisation de projets'}
        ]"
      />
    </v-col>
  </v-row>
</template>

<script>
import axios from 'axios'
import depts from '@/assets/data/departements-france.json'

const ddtDemos = [
  29, 22, 56, 35, 53, 72, 56, 44, 49, 37, 85, 79, 86, 17, 16, 87, 23, 19, 24, 33, 47, 40, 64,
  89, 58, 3, 15, 12, 48, 43, 30, 7, 26, 5, 69, '69M', '69D', 42, 63, 12, 48, 30, 84, 13, 4, 83, 6, 5,
  38, 73, 74, 39, 71, 21, 89, 58, 25, 70, 62, 60, 80, 2, 59, 976, 972
]

export default {
  props: {
    diffs: {
      type: Object,
      default () { return {} }
    }
  },
  data () {
    return { stats: {}, mapPoints: null }
  },
  async mounted () {
    await this.getNbAdmins()

    const { byDept: projectsByDept } = await this.getNbProjects()

    const mapDepts = {}

    depts.forEach((dept) => {
      const code = dept.code_departement

      let val = 0

      if (ddtDemos.includes(code)) {
        val = 1
      }

      const diff = this.diffs[code] || this.diffs[`0${code}`]

      if (diff && diff > 25) {
        val = 2
      }

      if (projectsByDept[code] || projectsByDept[`0${code}`]) {
        if (val === 2) {
          val = 3
        } // else { val = 2 }
      }

      mapDepts[code] = val
    })

    this.mapPoints = mapDepts
  },
  methods: {
    async getNbAdmins () {
      const { data } = await axios({
        url: '/api/stats/ddt',
        method: 'get'
      })

      // const ARA = depts.filter((dept) => {
      //   return dept.code_region === 84
      // })

      // const ARAprojects = { total: 0 }

      // ARA.forEach((dept) => {
      //   const nbProjects = data.byDept[dept.code_departement]

      //   ARAprojects[dept.nom_departement] = nbProjects.length
      //   ARAprojects.total += nbProjects.length
      // })

      // console.log(JSON.stringify(ARAprojects, null, 2))

      this.stats = data
    },
    async getNbProjects () {
      const { data } = await axios({
        url: '/api/stats/projects',
        method: 'get'
      })

      // console.log('data', data)

      return data
    }
  }
}
</script>
