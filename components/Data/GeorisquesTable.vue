<template>
  <v-data-table
    :headers="headers"
    :items="communesItems"
    :items-per-page="10"
    :footer-props="{'items-per-page-text':'commune par page'}"
    class="elevation-1"
  >
    <template #[`footer.page-text`]="items">
      {{ items.pageStart }} - {{ items.pageStop }} de {{ items.itemsLength }}
    </template>

    <!-- eslint-disable-next-line -->
    <template #item.actions="{ item }">
      <div class="d-flex" :style="{ justifyContent: 'end', alignItems: 'center', gap: '1rem' }">
        <v-btn color="primary" target="_blank" :href="item.urlGeoRisque">
          <v-icon
            small
            class="mr-2"
          >
            {{ icons.mdiLink }}
          </v-icon>
          Voir les risques
        </v-btn>
        <v-btn @click="download(item)">
          <v-icon
            small
            class="mr-2"
          >
            {{ icons.mdiDownload }}
          </v-icon>
          Télécharger les données PPR
        </v-btn>
        <v-tooltip top>
          <template #activator="{ on }">
            <v-btn
              v-if="selectable"
              color="primary"
              fab
              x-small
              v-on="on"
              @click="select(item)"
            >
              <v-icon>{{ isSelected(item) ? icons.mdiCheck : icons.mdiPlus }}</v-icon>
            </v-btn>
          </template>
          Ajouter la donnée à la section de PAC
        </v-tooltip>
      </div>
    </template>
  </v-data-table>
</template>

<script>
import { mdiLink, mdiDownload, mdiCheck, mdiPlus } from '@mdi/js'
import GEORISQUES_MAP from '@/assets/data/GeoRisquesMap.json'

export default {
  props: {
    communes: {
      type: Array,
      required: true
    },
    selectable: {
      type: Boolean,
      default: false
    },
    selection: {
      type: Array,
      default: () => []
    }
  },
  data () {
    return {
      icons: {
        mdiLink,
        mdiDownload,
        mdiCheck,
        mdiPlus
      },
      headers: [
        {
          text: 'Commune',
          value: 'intitule'
        },
        {
          text: 'Code INSEE',
          value: 'code'
        },
        { text: 'Actions', value: 'actions', sortable: false, align: 'center' }
      ],
      // selectedTheme: GEORISQUES_MAP[0].endpoint,
      dataset: [],
      themes: GEORISQUES_MAP
    }
  },
  computed: {
    communesItems () {
      return this.communes.map((e) => {
        const enriched = {
          ...e,
          urlGeoRisque: `https://www.georisques.gouv.fr/mes-risques/connaitre-les-risques-pres-de-chez-moi/rapport2?form-commune=true&codeInsee=${e.code}&city=${e.intitule}`
        }
        return enriched
      })
    }
  },
  // watch: {
  //   async selectedTheme (newVal) {
  //     const data = await this.$daturba.getGeorisques({
  //       dataset: newVal,
  //       insee: this.$route.query.insee
  //     })

  //     if (data.data.length > 0) {
  //       this.dataset = data.data.map((e, i) => ({
  //         champs: this.objToArr(data.data[i]),
  //         title: data.dataset
  //       }))
  //     } else {
  //       this.dataset = []
  //     }
  //   }
  // },
  methods: {
    async download (item) {
      const pprData = await this.$daturba.getGeorisques({
        dataset: 'ppr',
        insee: item.code
      })

      const text = JSON.stringify(pprData)
      const filename = `ppr_${item.intitule}.json`
      const element = document.createElement('a')
      element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(text))
      element.setAttribute('download', filename)

      element.style.display = 'none'
      document.body.appendChild(element)

      element.click()
      document.body.removeChild(element)
    },
    // objToArr (item) {
    //   const arr = []
    //   for (const [key, value] of Object.entries(item)) {
    //     arr.push({ nom: key, valeur: value })
    //   }
    //   return arr
    // },
    select (item) {
      if (this.isSelected(item)) {
        this.$emit('remove', item.urlGeoRisque)
      } else {
        this.$emit('add', {
          title: item.intitule,
          category: null,
          source: 'GEORISQUES',
          url: item.urlGeoRisque,
          links: null,
          extra: null
        })
      }
    },
    isSelected (item) {
      return !!this.selection.find(attachment => item.urlGeoRisque === attachment.url)
    }
  }
}
</script>
