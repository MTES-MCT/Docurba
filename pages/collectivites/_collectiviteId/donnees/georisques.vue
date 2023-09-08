<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12">
          <h1>Risques Géographique pour {{ communes && communes.length > 1 ? 'l\'Epci' : 'la commune' }} </h1>
        </v-col>
        <v-col cols="12">
          <p>
            Vous trouvez toutes les informations relatives aux risques sur le site georisques.gouv.fr.
            Vous pouvez également télécharger directement la donnée du Plan Prévention des Risques directement depuis Docurba.
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
                <v-btn color="primary" depressed class="mr-4" target="_blank" :href="item.urlGeoRisque">
                  <v-icon
                    small
                    class="mr-2"
                  >
                    {{ icons.mdiLink }}
                  </v-icon>
                  Voir les risques
                </v-btn>
                <!-- item.code_commune_INSEE, item.nom_commune -->
                <v-btn color="primary" depressed :loading="item.loading" @click="download(item)">
                  <v-icon
                    small
                    class="mr-2"
                  >
                    {{ icons.mdiDownload }}
                  </v-icon>
                  Télécharger les données PPR
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
  props: {
    isEpci: {
      type: Boolean,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    }
  },
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
        {
          text: 'Code Postal',
          value: 'code_postal'
        },
        {
          text: 'Code INSEE',
          value: 'code_commune_INSEE'
        },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      selectedTheme: GEORISQUES_MAP[0].endpoint,
      dataset: [],
      communes: null,
      themes: GEORISQUES_MAP,
      loading: true
    }
  },
  watch: {
    async selectedTheme (newVal) {
      console.log('selectedTheme: ', newVal)
      await this.getTheme()
    }
  },
  mounted () {
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

    let communesData
    if (this.isEpci) {
      communesData = this.collectivite.towns
    } else {
      communesData = [this.collectivite]
    }
    console.log('communesData: ', communesData)
    communesData = communesData.map((e) => {
      const enriched = {
        ...e,
        loading: false,
        // &typeForm=commune&postCode=${e.code_postal}
        urlGeoRisque: `https://www.georisques.gouv.fr/mes-risques/connaitre-les-risques-pres-de-chez-moi/rapport2?form-commune=true&codeInsee=${e.code_commune_INSEE}&city=${e.nom_commune}`
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

      const data = await this.$daturba.getGeorisques({
        dataset: this.selectedTheme,
        insee: this.$route.query.insee
      })

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
