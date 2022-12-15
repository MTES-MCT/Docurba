<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-chip-group
            v-model="selectedTheme"
            column
          >
            <v-chip
              v-for="theme in themes"
              :key="theme.endpoint"
              class="text-capitalize"
              :value="theme.endpoint"
              filter
              outlined
              color="bf500"
            >
              {{ theme.name }}
            </v-chip>
          </v-chip-group>
        </v-col>
        <v-col cols="12">
          {{ themes.find(e => e.endpoint === selectedTheme).description }}
        </v-col>
      </v-row>
    </v-container>
    <GeoIDECardList v-if="!loading" :region="currentRegion" :cards="dataset" :themes="[]" />
    <VGlobalLoader v-else />
  </div>
</template>

<script>
import GEORISQUES_MAP from '@/assets/data/GeoRisquesMap.json'

export default {
  data () {
    return {
      selectedTheme: GEORISQUES_MAP[0].endpoint,
      dataset: [],
      themes: GEORISQUES_MAP,
      loading: true
    }
  },
  computed: {
    currentRegion () {
      return this.$route.query.region
    }
  },
  watch: {
    async selectedTheme (newVal) {
      console.log('selectedTheme: ', newVal)
      await this.getTheme()
    }
  },
  async mounted () {
    // Start Analytics
    const inseeQuery = this.$route.query.insee
    const codes = typeof (inseeQuery) === 'object' ? inseeQuery : [inseeQuery]

    if (codes) {
      codes.forEach((code) => {
        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Georisques',
          `${this.$route.query.document} - ${code}`
        ])
      })
    }
    // End Analytics

    // const parsedInseeCode = codes.map((code) => {
    //   return `commune/${code.toString().length < 5 ? '0' + code : code}`
    // })

    // console.log('CODE: ', parsedInseeCode)

    // function objToArr (obj) {
    //   const arr = []
    //   for (const [key, value] of Object.entries(obj)) {
    //     console.log(`${key}: ${value}`)
    //     arr.push({ nom: key, valeur: value })
    //   }
    //   return arr
    // }
    // console.log('this.selectedTheme: ', this.selectedTheme)
    // const data = await this.$daturba.getGeorisques({ dataset: this.selectedTheme, insee: this.$route.query.insee })
    // console.log('Data Georisques: ', data)
    // if (data.data.length > 0) {
    //   this.dataset = [data].map(e => ({ champs: objToArr(data.data[0]), title: data.dataset }))
    // }
    await this.getTheme()
    this.loading = false
  },
  methods: {
    async getTheme () {
      function objToArr (obj) {
        const arr = []
        for (const [key, value] of Object.entries(obj)) {
          console.log(`${key}: ${value}`)
          arr.push({ nom: key, valeur: value })
        }
        return arr
      }
      console.log('this.selectedTheme: ', this.selectedTheme)
      const data = await this.$daturba.getGeorisques({ dataset: this.selectedTheme, insee: this.$route.query.insee })
      console.log('Data Georisques: ', data)
      if (data.data.length > 0) {
        this.dataset = data.data.map((e, i) => ({ champs: objToArr(data.data[i]), title: data.dataset }))
      } else {
        this.dataset = []
      }
    }
  }
}
</script>
