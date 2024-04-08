<template>
  <div>
    <iframe v-if="iframeSrc" :src="iframeSrc" title="GeoBretagneViewer" />
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
    const centerRes = await axios.get(`/api/geo/collectivites/${this.collectiviteCode}/center`)

    const [x4326, y4326] = centerRes.data.coordinates

    const { x, y } = this.epsg4326toEpsg3857(x4326, y4326)

    const xss = '%3Cscript%3EsetTimeout%28%28%29%3D%3E%7B%24%28%27%23help%27%29.hide%28%29%3B%24%28%27.modal-backdrop%27%29.hide%28%29%3B%24%28%27%23legend%27%29.removeClass%28%27active%27%29%3B%7D%2C2000%29%3C%2Fscript%3E'
    this.iframeSrc = `https://geobretagne.fr/mviewer/?x=${x}&y=${y}&z=13&config=/apps/viz/config.xml&title=${xss}`

    this.$analytics({
      category: 'public',
      name: 'afficher carte',
      value: this.collectiviteCode
    })
  },
  methods: {
    epsg4326toEpsg3857 (lon, lat) {
      const x = (lon * 20037508.34) / 180
      let y = Math.log(Math.tan(((90 + lat) * Math.PI) / 360)) / (Math.PI / 180)
      y = (y * 20037508.34) / 180
      return { x, y }
    }
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
