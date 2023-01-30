<template>
  <div>
    <!-- <v-container>
      <v-row>
        <v-col cols="12">
          <v-chip-group v-model="selectedTheme" column>
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
          {{ themes.find((e) => e.endpoint === selectedTheme).description }}
        </v-col>
      </v-row>
    </v-container> -->
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1>Risques Géographique pour {{ communes && communes.length > 1 ? 'l\'Epci' : 'la commune' }} </h1>
        </v-col>
      </v-row>
      <v-row v-if="communes">
        <v-col
          v-for="(card, i) in communes"
          :key="`${card.title}-${i}`"
          cols="6"
        >
          <v-card flat outlined>
            <v-card-title class="break-word">
              Georisques {{ card.nom_commune }}
            </v-card-title>
            <v-card-text>
              Vous trouvez toutes les informations relatives aux risques sur le site georisques.gouv.fr.
              <br>
              Vous pouvez également télécharger directement la donnée du Plan Prévention des Risques directement depuis Docurba.
              <!-- {{ card.ppr }} -->
            </v-card-text>
            <v-card-actions>
              <v-btn target="_blank" :href="card.urlGeoRisque" color="primary">
                Voir les risques
              </v-btn>
              <v-btn color="primary" @click=" download (card.ppr, card.nom_commune)">
                Télécharger les données PPR
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
      <v-row v-else>
        <VGlobalLoader />
      </v-row>
    </v-container>
    <!-- <GeoIDECardList
      v-if="!loading"
      :region="currentRegion"
      :cards="dataset"
      :themes="[]"
    /> -->
    <!-- <VGlobalLoader v-else /> -->
  </div>
</template>

<script>
import GEORISQUES_MAP from '@/assets/data/GeoRisquesMap.json'

export default {
  data () {
    return {
      selectedTheme: GEORISQUES_MAP[0].endpoint,
      dataset: [],
      communes: null,
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
    const codes = typeof inseeQuery === 'object' ? inseeQuery : [inseeQuery]

    if (codes) {
      codes.forEach((code) => {
        this.$matomo([
          'trackEvent',
          'Socle de PAC',
          'Georisques',
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
    let communesData = await this.$daturba.getCommunesDetails(
      Array.isArray(this.$route.query.insee) ? this.$route.query.insee : [this.$route.query.insee]
    )

    const promsPpr = []
    communesData = communesData.map((e) => {
      const pprData = this.$daturba.getGeorisques({
        dataset: 'ppr',
        insee: e.code_commune_INSEE
      })
      promsPpr.push(pprData)
      const enriched = {
        ...e,
        urlGeoRisque: `https://www.georisques.gouv.fr/mes-risques/connaitre-les-risques-pres-de-chez-moi/rapport2?form-commune=true&codeInsee=${e.code_commune_INSEE}&city=${e.nom_commune}&typeForm=commune&postCode=${e.code_postal}`,
        ppr: pprData
      }
      return enriched
    })
    const pprs = await Promise.all(promsPpr)
    communesData = communesData.map((e, i) => ({
      ...e,
      ppr: pprs[i]
    }))
    this.communes = communesData

    // await this.getTheme()
    this.loading = false
  },
  methods: {
    download (jsonData, name) {
      const text = JSON.stringify(jsonData)
      const filename = `ppr_${name}.json`
      const element = document.createElement('a')
      element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(text))
      element.setAttribute('download', filename)

      element.style.display = 'none'
      document.body.appendChild(element)

      element.click()
      document.body.removeChild(element)
    },
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
      const data = await this.$daturba.getGeorisques({
        dataset: this.selectedTheme,
        insee: this.$route.query.insee
      })
      console.log('Data Georisques: ', data)
      if (data.data.length > 0) {
        this.dataset = data.data.map((e, i) => ({
          champs: objToArr(data.data[i]),
          title: data.dataset
        }))
      } else {
        this.dataset = []
      }
    }
  }
}
</script>
