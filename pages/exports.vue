<template>
  <v-container>
    <v-row align="center">
      <v-col cols="">
        <v-text-field v-model="departementCode" :hint="`${requestTime} sec`" persistent-hint filled small />
      </v-col>
      <v-col cols="auto">
        <v-btn
          color="principal"
          depressed
          tile
          :loading="loading"
          @click="fetchCommunes"
        >
          Fetch
        </v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-textarea
          v-model="communeJSON"
          outlined
          readonly
          auto-grow
          persistent-hint
          :hint="`found ${allData.length} communes`"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'
export default {
  layout: 'ddt',
  data () {
    return {
      departementCode: '01',
      allData: [],
      json: {},
      timer: 0,
      loading: false
    }
  },
  computed: {
    communeJSON () {
      return JSON.stringify(this.json, null, 4)
    },
    requestTime () {
      return Math.round(this.timer / 1000).toString()
    }
  },
  methods: {
    async fetchCommunes () {
      this.loading = true
      this.timer = +new Date()
      const { data: communesData } = await axios(`/api/urba/exports/departements/${this.departementCode}`)
      this.timer = +new Date() - this.timer
      this.allData = communesData
      this.json = communesData[0]

      this.loading = false
    }
  }
}
</script>
