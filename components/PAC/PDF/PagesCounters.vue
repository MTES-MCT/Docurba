<template>
  <div class="page-counters-container">
    <div ref="page" class="page-sizer">
      <div ref="content" class="content-sizer" />
    </div>
    <div
      v-for="(counter, i) in pageCounters"
      :key="i"
      :style="counter.style"
      class="page-counter"
    >
      {{ counter.text }}
    </div>
  </div>
</template>

<script>

export default {
  props: {
    // eslint-disable-next-line vue/prop-name-casing
    contentId: {
      type: String,
      default: 'pac-content-pdf'
    },
    pacData: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      pageCounters: []
    }
  },
  mounted () {
    this.$nextTick(() => {
      const contentEl = document.getElementById(this.contentId)

      // console.log(this.$refs.rootsEl)
      // const pageHeight = this.$refs.page.offsetHeight
      const contentHeight = this.$refs.content.offsetHeight
      const nbPages = (contentEl.offsetHeight / contentHeight) + this.pacData.length

      const elRect = contentEl.getBoundingClientRect()
      const topPosition = elRect.top

      const nbTopPage = Math.ceil(topPosition / contentHeight)

      for (let page = 0; page < nbPages; page++) {
        const topPos = (nbTopPage * 263) + (page * 263) + 256

        this.pageCounters.push({
          text: `${page + 1} / ${Math.ceil(nbPages)}`,
          style: {
            top: `${topPos}mm`
            // top: `calc(${nbTopPage * 263}mm + ${255 + page * 263}mm)`
            // top: `${255 + page * 263}mm`
          }
        })
      }
    })
  }
}
</script>

<style scoped>
.page-sizer {
  min-height: 297mm;
  height: 297mm;
  position: absolute;
}

.content-sizer {
  /* min-height: 297mm;
  height: 297mm; */
  min-height: 254.5mm;
  height: 254.5mm;
  position: absolute;
}

.page-counters-container {
  position: relative;
  height: 0px;
}

 .page-counter {
  position: absolute;
  right: 0px;
 }
</style>
