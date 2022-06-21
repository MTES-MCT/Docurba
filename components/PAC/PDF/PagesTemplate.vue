<template>
  <div class="root-container text-justify">
    <PACPDFSectionTemplate
      v-for="root in PACroots"
      :key="root.path"
      ref="rootsEl"
      :section="root"
      class="print-root"
    />
    <div
      v-for="(counter, i) in pageCounters"
      :key="i"
      :style="counter.style"
      class="page-counter"
    >
      {{ counter.text }}
    </div>
    <div ref="content" class="content-sizer" />
    <div ref="page" class="page-sizer" />
  </div>
</template>

<script>
import pacContent from '@/mixins/pacContent.js'

export default {
  mixins: [pacContent],
  data () {
    return {
      pageCounters: []
    }
  },
  computed: {
    PACroots () {
      const roots = this.PAC.filter(section => section.depth === 2).sort((sa, sb) => {
        return sa.ordre - sb.ordre
      })

      return roots
    }
  },
  mounted () {
    this.$nextTick(() => {
      // console.log(this.$refs.rootsEl)
      // const pageHeight = this.$refs.page.offsetHeight
      const contentHeight = this.$refs.content.offsetHeight
      const nbPages = (this.$el.offsetHeight / contentHeight) + this.PACroots.length - 1

      const elRect = this.$el.getBoundingClientRect()
      const topPosition = elRect.top

      const nbTopPage = Math.ceil(topPosition / contentHeight)

      for (let page = 0; page < nbPages; page++) {
        this.pageCounters.push({
          text: `${page + 1} / ${Math.ceil(nbPages)}`,
          style: {
            top: `calc(${nbTopPage * 263}mm + ${255 + page * 263}mm)`
            // top: `${255 + page * 263}mm`
          }
        })
      }
    })
  }
}
</script>

<style scoped>
 .print-root {
   /* page-break-after: always; */
   page-break-inside: avoid;
 }

/* tr {
  page-break-after: always;
} */

 .root-container {
   page-break-inside: avoid;
 }

 .page-counter {
  position: absolute;
  right: 0px;
 }

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
</style>
