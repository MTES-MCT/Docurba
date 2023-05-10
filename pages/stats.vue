<template>
  <v-container class="my-8">
    <v-row justify="center" align="center">
      <v-col cols="12">
        <v-card min-height="200px">
          <template v-if="nbEdits && nbEdits.length">
            <v-card-title class="break-word">
              Un total de {{ sum(nbEdits) }} editions de PAC ont été faites sur Docurba
            </v-card-title>
            <v-card-text>
              <v-sparkline
                :value="nbEdits"
                color="primary"
                height="100"
                padding="24"
                stroke-linecap="round"
                line-width="2"
                smooth
              >
                <template #label="item">
                  {{ edits[item.index].month }}
                </template>
              </v-sparkline>
            </v-card-text>
          </template>
          <v-card-text v-else>
            <v-row class="card-loader" justify="center" align="center">
              <v-progress-circular color="primary" indeterminate />
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="6">
        <v-card>
          <v-card-title class="break-word">
            Nombre d'agents de DDT/DEAL ayant rejoint Docurba
          </v-card-title>
          <v-card-text class="text-center primary--text py-16">
            <span v-if="nbAgents" class="big-number">
              {{ nbAgents }}
            </span>
            <v-progress-circular v-else color="primary" indeterminate />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card>
          <v-card-title class="break-word">
            Nombre de communes couvertes par Docurba
          </v-card-title>
          <v-card-text class="text-center primary--text py-16">
            <span class="big-number">
              4467
            </span>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card>
          <v-card-title class="break-word">
            {{ sum(nbVisits) }} visites sur les 30 derniers jours
          </v-card-title>
          <v-card-text>
            <v-sparkline
              :value="nbVisits"
              color="primary"
              height="100"
              padding="24"
              stroke-linecap="round"
              line-width="2"
              smooth
            >
              <!-- <template #label>
                <tspan>
                  06/22
                </tspan>
              </template> -->
            </v-sparkline>
          </v-card-text>
          <v-card-subtitle class="text-center">
            <a href="https://stats.data.gouv.fr/index.php?module=CoreHome&action=index&idSite=235&period=range&date=previous30#?period=range&date=previous30&category=Dashboard_Dashboard&subcategory=1&idSite=235" target="_blank">
              Plus d'informations sur notre page matomo
            </a>
          </v-card-subtitle>
        </v-card>
      </v-col>
      <v-col cols="6">
        <v-card>
          <v-card-title class="break-word">
            En moyenne {{ Math.round((sum(nbVisitors)/30)*10)/10 }} visiteurs par jour
          </v-card-title>
          <v-card-text>
            <v-sparkline
              :value="nbVisitors"
              color="primary"
              height="100"
              padding="24"
              stroke-linecap="round"
              line-width="2"
              smooth
            >
              <!-- <template #label>
                <tspan>
                  06/22
                </tspan>
              </template> -->
            </v-sparkline>
          </v-card-text>
          <v-card-subtitle class="text-center">
            <a href="https://stats.data.gouv.fr/index.php?module=CoreHome&action=index&idSite=235&period=range&date=previous30#?period=range&date=previous30&category=Dashboard_Dashboard&subcategory=1&idSite=235" target="_blank">
              Plus d'informations sur notre page matomo
            </a>
          </v-card-subtitle>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      edits: [],
      nbVisits: [],
      nbVisitors: [],
      weekLabels: [],
      nbAgents: null
    }
  },
  computed: {
    nbEdits () {
      return this.edits.map((month) => {
        return month.value
      })
    }
  },
  async mounted () {
    const date = this.$dayjs().subtract(1, 'day')
    const lastMonth = date.subtract(30, 'day')

    const dateRange = `${lastMonth.format('YYYY-MM-DD')},${date.format('YYYY-MM-DD')}`

    // console.log(dateRange)

    const { data: visits, err } = await axios({
      url: `https://stats.data.gouv.fr/index.php?module=API&format=JSON&idSite=235&period=day&date=${dateRange}&method=API.get&filter_limit=-1&format_metrics=1&expanded=1&token_auth=anonymous&force_api_session=1`,
      method: 'get'
    })

    this.getEvents()

    console.log(visits)

    if (!err) {
      const days = Object.keys(visits).sort((d1, d2) => {
        return this.$dayjs(d1, 'YYYY-MM-DD') - this.$dayjs(d2, 'YYYY-MM-DD')
      })

      // console.log(visits)

      this.nbVisits = days.map(day => visits[day].nb_visits || 0)
      this.nbVisitors = days.map(day => visits[day].nb_uniq_visitors || 0)

      this.getEdits()
      this.getNbAdmins()
      this.getNbProjects()
      this.getPACsDiff()
      this.getFDR()
    }
  },
  methods: {
    async getEdits () {
      const { data: edits, err } = await axios({
        url: '/api/stats/edits',
        method: 'get'
      })

      if (!err) {
        this.edits = edits
      }
    },
    async getNbAdmins () {
      const { data } = await axios({
        url: '/api/stats/ddt',
        method: 'get'
      })

      console.log(data)

      this.nbAgents = data.nbAdmins
    },
    async getNbProjects () {
      const { data: nbProjects } = await axios({
        url: '/api/stats/projects',
        method: 'get'
      })

      console.log(nbProjects)
    },
    async getEvents () {
      const date = this.$dayjs().subtract(30, 'day')
      const lastMonth = date.subtract(90, 'day')

      const dateRange = `${lastMonth.format('YYYY-MM-DD')},${date.format('YYYY-MM-DD')}`

      const { data: eventsData, err } = await axios({
        url: `https://stats.data.gouv.fr/index.php?module=API&format=JSON&idSite=235&period=day&date=${dateRange}&method=Events.getCategory&secondaryDimension=eventAction&flat=1&token_auth=anonymous&force_api_session=1`
      })

      if (!err) {
        console.log(eventsData)
      } else {
        console.log(err)
      }
    },
    async getPACsDiff () {
      const { data: diffs } = await axios({
        url: '/api/stats/diff',
        method: 'get'
      })

      console.log('diff', diffs)
    },
    async getFDR () {
      const { data: fdr } = await axios({
        url: '/api/stats/fdr',
        method: 'get'
      })

      console.log('fdr', fdr)
    },
    sum (values) {
      return values.reduce((total, val) => {
        return total + val
      }, 0)
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
