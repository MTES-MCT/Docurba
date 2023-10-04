<template>
  <div>
    <iframe v-if="iframeSrc" :src="iframeSrc" />
  </div>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    collectiviteCode: {
      type: String,
      required: true
    },
    isEpci: {
      type: Boolean,
      required: true
    }
  },
  data () {
    return {
      iframeSrc: null
    }
  },
  async created () {
    const centerRes = await axios.get(`https://geo.api.gouv.fr/${this.isEpci ? 'epcis' : 'communes'}/${this.collectiviteCode}?fields=centre`)

    const [x4326, y4326] = centerRes.data.centre.coordinates

    const transformRes = await axios.get('https://epsg.io/trans', {
      params: {
        x: x4326,
        y: y4326,
        s_srs: '4326',
        t_srs: '3857'
      }
    })

    const { x, y } = transformRes.data

    const xss = '%3Cscript%3EsetTimeout%28%28%29%3D%3E%7B%24%28%27%23help%27%29.hide%28%29%3B%24%28%27.modal-backdrop%27%29.hide%28%29%3B%24%28%27%23legend%27%29.removeClass%28%27active%27%29%3B%7D%2C2000%29%3C%2Fscript%3E'
    this.iframeSrc = `https://geobretagne.fr/mviewer/?x=${x}&y=${y}&z=13&config=/apps/viz/config.xml&title=${xss}`
  }
}
</script>

<style scoped>
iframe {
  width: 100%;
  height: 800px;
  border: none;
}
</style>
