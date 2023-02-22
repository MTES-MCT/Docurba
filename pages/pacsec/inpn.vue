<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1>INPN pour {{ communes && communes.length > 1 ? 'l\'Epci' : 'la commune' }} </h1>
        </v-col>
        <v-col cols="12">
          <p>
            Vous trouvez toutes les informations relatives à l'Inventaire National du Patrimoine Naturel surle site inpn.mnhn.fr.
          </p>
        </v-col>
      </v-row>
      <v-row v-if="communes">
        <v-col cols="12">
          <v-data-table
            :headers="headers"
            :items="communes"
            :items-per-page="10"
            :footer-props="{'items-per-page-text':'commune par page'}"
            class="elevation-1"
          >
            <template #[`footer.page-text`]="items">
              {{ items.pageStart }} - {{ items.pageStop }} de {{ items.itemsLength }}
            </template>

            <!-- eslint-disable-next-line -->
            <template #item.actions="{ item }">
              <div class="">
                <v-btn color="primary" text class="mr-4 my-2" target="_blank" :href="item.urlEspaces">
                  <v-icon
                    small
                    class="mr-2"
                  >
                    {{ icons.mdiLink }}
                  </v-icon>
                  Esp. protégés
                </v-btn>
                <v-btn color="primary" text class="mr-4 my-2" target="_blank" :href="item.urlZnieff">
                  <v-icon
                    small
                    class="mr-2"
                  >
                    {{ icons.mdiLink }}
                  </v-icon>
                  Znieff
                </v-btn>
                <v-btn color="primary" text class="mr-4 my-2" target="_blank" :href="item.urlInpg">
                  <v-icon
                    small
                    class="mr-2"
                  >
                    {{ icons.mdiLink }}
                  </v-icon>
                  INPG
                </v-btn>
                <v-btn color="primary" text class="mr-4 my-2" target="_blank" :href="item.urlNatura2000">
                  <v-icon
                    small
                    class="mr-2"
                  >
                    {{ icons.mdiLink }}
                  </v-icon>
                  Natura 2000
                </v-btn>
                <v-btn color="primary" text class="mr-4 my-2" target="_blank" :href="item.urlArcheo">
                  <v-icon
                    small
                    class="mr-2"
                    color="primary"
                  >
                    {{ icons.mdiLink }}
                  </v-icon>
                  Archéologiques
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
      <v-row v-else>
        <VGlobalLoader />
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { mdiLink, mdiDownload } from '@mdi/js'
import GEORISQUES_MAP from '@/assets/data/GeoRisquesMap.json'

export default {
  name: 'Georisque',
  data () {
    return {
      icons: {
        mdiLink,
        mdiDownload
      },
      headers: [
        {
          text: 'Commune',
          value: 'nom_commune'
        },
        // {
        //   text: 'Code Postal',
        //   value: 'code_postal'
        // },
        // {
        //   text: 'Code INSEE',
        //   value: 'code_commune_INSEE'
        // },
        { text: 'Liens', value: 'actions', sortable: false, align: 'center' }
      ],
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

    communesData = communesData.map((e) => {
      const toto = '22'.padStart(8, '0')
      console.log('toto: ', toto, ' ', e.code_commune_INSEE)
      const urlInpn = `https://inpn.mnhn.fr/collTerr/commune/${e.code_commune_INSEE.toString().padStart(5, '0')}`
      const enriched = {
        ...e,
        loading: false,
        urlEspaces: `${urlInpn}/tab/espaces`,
        urlZnieff: `${urlInpn}/tab/znieff`,
        urlInpg: `${urlInpn}/tab/inpg`,
        urlNatura2000: `${urlInpn}/tab/natura2000`,
        urlArcheo: `${urlInpn}/tab/archeo`
      }
      return enriched
    })
    this.communes = communesData
    this.loading = false
  },
  methods: {
    async download (commune) {
      try {
        commune.loading = true
        const pprData = await this.$daturba.getGeorisques({
          dataset: 'ppr',
          insee: commune.code_commune_INSEE
        })
        console.log('pprData: ', pprData)
        const text = JSON.stringify(pprData)
        const filename = `ppr_${commune.nom_commune}.json`
        const element = document.createElement('a')
        element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(text))
        element.setAttribute('download', filename)

        element.style.display = 'none'
        document.body.appendChild(element)

        element.click()
        document.body.removeChild(element)
        commune.loading = false
      } catch (error) {
        console.log('Error: ', error)
      }
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
