<template>
  <v-row justify="center">
    <v-col cols="12">
      <h2 class="text-h2">
        Accès au contenu du socle de PAC :
      </h2>
      <p>
        Indicateur sur les collectivités guidées grâce au contenu disponible en amont, dès leur lancement dans l’élaboration de leur document d’urbanisme. Contenu à 2 niveaux : cadre juridique national, éléments régionaux (SRADDET & doctrine régionale).
      </p>
    </v-col>
    <v-col cols="12" md="6">
      <!-- <StatsBignumberCard title="Nombre de consultations du cadre juridique" :number="stats.nbContent" /> -->
      <StatsBarsCard title="Répartition des contenus consultés" :points="stats.pacBars" />
    </v-col>
    <v-col cols="12" md="6">
      <!-- <StatsDonutCard title="Répartition des contenus consultés : Cadre juridique" :number="percentContent" /> -->
      <StatsLineCard title="Nombre de consultations des contenus du PAC" :points="stats.soclePoints" />
    </v-col>
    <v-col cols="12" md="6">
      <!-- <StatsBignumberCard title="Nombre de consultations des jeux de données" :number="stats.nbData" /> -->
      <StatsLineCard title="Nombre de consultations des jeux de données" :points="stats.dataPoints" />
    </v-col>
    <!-- <v-col cols="12" md="6">
      <StatsDonutCard title="Répartition des contenus consultés : Jeux de données" :number="100-percentContent" />
    </v-col> -->
  </v-row>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      stats: {},
      percentContent: null
    }
  },
  mounted () {
    this.getEvents()
  },
  methods: {
    async getEvents () {
      const date = this.$dayjs().subtract(30, 'day')
      const lastMonth = date.subtract(180, 'day')

      const dateRange = `${lastMonth.format('YYYY-MM-DD')},${date.format('YYYY-MM-DD')}`

      const { data: eventsData } = await axios({
        url: `https://stats.data.gouv.fr/index.php?module=API&format=JSON&idSite=235&period=day&date=${dateRange}&method=Events.getCategory&secondaryDimension=eventAction&flat=1&token_auth=anonymous&force_api_session=1`
      })

      const { data: categData } = await axios({
        url: `https://stats.data.gouv.fr/index.php?module=API&format=JSON&idSite=235&period=day&date=${dateRange}&method=Events.getCategory&secondaryDimension=eventName&flat=1&token_auth=anonymous&force_api_session=1`
      })

      const days = Object.keys(eventsData).sort((d1, d2) => {
        return this.$dayjs(d1, 'YYYY-MM-DD') - this.$dayjs(d2, 'YYYY-MM-DD')
      })

      const eventsCounts = {}

      days.forEach((day) => {
        const events = eventsData[day]

        events.forEach((eventData) => {
          if (!eventsCounts[eventData.label]) {
            eventsCounts[eventData.label] = 0
          }

          eventsCounts[eventData.label] += (eventData.nb_events || 0)
        })
      })

      const categCounts = {}

      days.forEach((day) => {
        const events = categData[day]

        events.forEach((eventData) => {
          if (!categCounts[eventData.label]) {
            categCounts[eventData.label] = 0
          }

          categCounts[eventData.label] += (eventData.nb_events || 0)
        })
      })

      const pacBars = Object.keys(eventsCounts).filter(key => key.includes('Socle de PAC')).map((key) => {
        return {
          x: key.replace('Socle de PAC - ', ''),
          xLabel: key.replace('Socle de PAC - ', ''),
          y: eventsCounts[key],
          yLabel: eventsCounts[key]
        }
      })

      const dataBars = Object.keys(categCounts).filter(key => key.includes('PAC Content -')).map((key) => {
        return {
          x: key.replace('PAC Content - ', ''),
          xLabel: key.replace('PAC Content - ', ''),
          y: categCounts[key],
          yLabel: categCounts[key]
        }
      })

      // console.log('events', eventsCounts, categCounts, eventsData, categData)

      const soclePoints = days.map((day) => {
        const events = eventsData[day]

        const y = events.reduce((yVal, e) => {
          return yVal + (e.label.includes('Content') ? e.nb_events : 0)
        }, 0)

        return {
          x: new Date(this.$dayjs(day, 'YYYY-MM-DD').format()),
          y
        }
      })

      const dataPoints = days.map((day) => {
        const events = eventsData[day]

        const y = events.reduce((yVal, e) => {
          return yVal + (e.label.includes('Data') ? e.nb_events : 0)
        }, 0)

        return {
          x: new Date(this.$dayjs(day, 'YYYY-MM-DD').format()),
          y
        }
      })

      const nbContent = eventsCounts['PAC Content - Open Section'] + eventsCounts['Socle de PAC - Content']
      const nbData = eventsCounts['Data Source - Carte'] + eventsCounts['Projet PAC - Data']

      this.percentContent = Math.round((nbContent / (nbContent + nbData)) * 100)

      // this.nbVisits = days.map(day => visits[day].nb_visits || 0)
      // this.nbVisitors = days.map(day => visits[day].nb_uniq_visitors || 0)

      this.stats = {
        pacBars,
        dataBars,
        soclePoints,
        dataPoints,
        nbContent,
        nbData
      }
    }
  }
}
</script>
