<template>
  <v-container>
    <v-row align="center">
      <v-col cols="">
        <v-text-field v-model="departementCode" :hint="`${requestTime} sec`" persistent-hint filled small />
      </v-col>
      <v-col cols="auto">
        <v-checkbox v-model="asCsv" label="csv" />
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
          v-model="displayedText"
          outlined
          readonly
          auto-grow
          persistent-hint
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
      displayedText: '',
      asCsv: false,
      timer: 0,
      loading: false
    }
  },
  computed: {
    requestTime () {
      return Math.round(this.timer / 1000).toString()
    }
  },
  methods: {
    async fetchCommunes () {
      this.loading = true
      const start = +new Date()
      const { data: communesData } = await axios(`/api/urba/exports/departements/${this.departementCode}?csv=${this.asCsv}`)
      this.timer = +new Date() - start

      if (this.asCsv) {
        this.displayedText = communesData
      } else {
        this.displayedText = JSON.stringify(communesData[0], null, 4)
      }

      this.loading = false
    }
  }
}
</script>
