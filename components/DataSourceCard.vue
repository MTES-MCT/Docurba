<template>
  <v-card flat color="g100">
    <v-card-title class="break-word">
      {{ source.nom }}
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col v-if="subTheme" cols="12">
          <v-chip
            outlined
            class="text-capitalize"
            color="bf300"
          >
            {{ subTheme.text }}
          </v-chip>
        </v-col>
      </v-row>
      <v-row class="py-4">
        <v-col v-for="(ressource, i) in source.ressources" :key="i" cols="12" class="py-0">
          <v-btn text color="primary" :href="ressource.valeur" target="_blank">
            <v-icon small class="mr-2">
              {{ icons.mdiOpenInNew }}
            </v-icon>
            {{ ressource.alias }}
          </v-btn>
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-dialog height="600px" width="900px">
        <template #activator="{on}">
          <v-btn block depressed color="primary" v-on="on">
            <v-icon class="pr-2">
              {{ icons.mdiMap }}
            </v-icon>
            Voir la carte
          </v-btn>
        </template>
        <v-card height="600px" width="900px">
          <iframe width="900" height="600" :src="source.carto_url" />
        </v-card>
      </v-dialog>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mdiOpenInNew, mdiMap } from '@mdi/js'

// import axios from 'axios'

export default {
  props: {
    source: {
      type: Object,
      required: true
    },
    subTheme: {
      type: Object,
      default () { return {} }
    }
  },
  data () {
    return {
      icons: {
        mdiOpenInNew,
        mdiMap
      },
      iframeLoading: true
    }
  },
  mounted () {
    console.log(this.source)

    // const dataContext = (await axios({
    //   url: 'https://carto.datara.gouv.fr/carto/context?account=1&contextPath=/layers/ea091248-ad5f-4759-b9d3-9b3e8c5020de.map&object=AOCviticoleAiresparcellairesARA%3Bgid%3B130',
    //   method: 'get',
    //   headers: {
    //     Authorization: 'Basic ' + window.btoa('demo:p@55w0rd')
    //   }
    // })).data

    // console.log(dataContext)

    // const imageLayers = [
    //   'https://carto.datara.gouv.fr/carto/context?account=1&contextPath=/layers/ea091248-ad5f-4759-b9d3-9b3e8c5020de.map&object=AOCviticoleAiresparcellairesARA%3Bgid%3B130',
    //   'https://datacarto.datara.gouv.fr/map/layers/ea091248-ad5f-4759-b9d3-9b3e8c5020de?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&FORMAT=image%2Fpng&TRANSPARENT=true&LAYERS=layer2&CRS=EPSG%3A2154&STYLES=&WIDTH=2650&HEIGHT=1144&BBOX=899413.764757217%2C6518557.533808398%2C905452.8052427833%2C6521164.576191601'
    // ].map((url) => {
    //   return new Promise((resolve) => {
    //     const img = new Image()
    //     img.addEventListener('load', () => resolve(img))
    //     img.src = url
    //   })
    // })

    // const context = this.$refs.canvas.getContext('2d')

    // Promise.all(imageLayers).then((layers) => {
    //   console.log('images loaded')

    //   layers.forEach((layer) => {
    //     context.drawImage(layer, 0, 0, 500, 500)
    //   })

    //   this.iframeLoading = false
    // })
  },
  methods: {
    showIframe () {
      // setTimeout(() => {
      // this.iframeLoading = false
      // }, 500)

      // console.log('QS - ', this.$refs.sourceIframe)

      // const iframeDoc = this.$refs.sourceIframe.contentWindow.document

      // console.log('QS -', iframeDoc)

      // iframeDoc.getElementById('title-nav').remove()
      // iframeDoc.getElementById('mobile-actions').remove()
    }
  }
}
</script>
