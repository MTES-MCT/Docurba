<template>
  <div class="page-counters-container">
    <div ref="page" class="page-sizer">
      <div ref="margin" class="margin-sizer" />
      <div ref="content" class="content-sizer" :style="{top: `${topPos}mm`}" />
    </div>
    <div
      v-for="(counter, i) in pageCounters"
      :key="i"
      :style="counter.style"
      class="page-counter"
    >
      {{ counter.text }}
    </div>
    <!-- <div v-for="(debugLine, i) in debugLines" :key="`${debugLine.top} ${i}`" :style="Object.assign({}, debugLine, {marginTop: `-${debugLine.initialSpaceLeft}px`, borderColor: 'blue', color: 'blue' })" class="debug-line break-line">
      <b>{{ debugLine.accumulatedHeight - debugLine.initialSpaceLeft }} - {{ debugLine.from }}</b>
    </div>
    <div v-for="debugLine in debugLines" :key="debugLine.top" :style="debugLine" class="debug-line">
      <b>{{ debugLine.accumulatedHeight }} - {{ debugLine.from }}</b>
    </div>
    <div :style="{top: finalLine}" class="debug-line final-line">
      <b>{{ finalLine }}</b>
    </div> -->
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
      pageCounters: [],
      debugLines: [],
      finalLine: 0,
      topPos: 0
    }
  },
  mounted () {
    // We use contentHeight instead of full page to acocunt for global margins.
    // const pageHeight = this.$refs.page.offsetHeight
    const marginHeight = this.$refs.margin.offsetHeight
    const pageHeight = this.$refs.content.offsetHeight
    // console.log(pageHeight)

    function calculateElementHeight (element) {
      const { paddingTop, paddingBottom, marginTop, marginBottom } = getComputedStyle(element)
      const contentHeight = element.offsetHeight
      const margins = parseFloat(paddingTop) + parseFloat(paddingBottom) +
        parseFloat(marginTop) + parseFloat(marginBottom)

      return { height: contentHeight + margins, margins, marginBottom: parseFloat(marginBottom) }
    }

    const initialHeight = 0 // + 10
    let accumulatedHeight = initialHeight
    const debugLines = []

    function getSpaceLeft () {
      return pageHeight - (accumulatedHeight % pageHeight)
    }

    function addBreakPoint (from) {
      const initialSpaceLeft = getSpaceLeft()
      accumulatedHeight += (initialSpaceLeft === pageHeight ? 0 : initialSpaceLeft)

      debugLines.push({
        initialSpaceLeft,
        top: accumulatedHeight,
        borderColor: 'green',
        from
      })

      // console.log(accumulatedHeight, accumulatedHeight % pageHeight, Math.ceil(accumulatedHeight / (pageHeight)))

      const endSpaceLeft = getSpaceLeft()

      // eslint-disable-next-line no-console
      // console.log('add break point', from, accumulatedHeight % pageHeight, initialSpaceLeft, accumulatedHeight)

      return endSpaceLeft
    }

    function traverseElements (element) {
      const {
        height, margins
        // marginBottom
      } = calculateElementHeight(element)
      const isRoot = element.classList.value.includes('print-root')
      let spaceLeft = getSpaceLeft()

      if (element.tagName === 'TEXTAREA') { return }

      // console.log(height, margins)

      // ROOT HANDLING
      if (isRoot && accumulatedHeight > initialHeight) {
        spaceLeft = addBreakPoint('root')
        // accumulatedHeight += 10
      }
      // END ROOT HANDLING

      if (element.tagName !== 'DIV' && height < spaceLeft) {
        // console.log('skip', element, height, margins)
        accumulatedHeight += height
      } else {
        const children = element.children
        if (children && children.length && element.tagName !== 'P' && element.tagName !== 'LI') {
          for (let i = 0; i < children.length; i++) {
            traverseElements(children[i])
          }

          // Handle parent margin because not taking into account in child.
          spaceLeft = getSpaceLeft()

          if (margins >= spaceLeft) {
            spaceLeft = addBreakPoint(`${element.tagName} - ${element.innerText.slice(0, 30)}`)
          }

          accumulatedHeight += margins
        } else if (element.tagName === 'IMG' || element.tagName[0] === 'H') {
          if (element.tagName === 'IMG') { console.log('image', height) }
          addBreakPoint(`IMG & H - ${element.src || element.innerText.slice(0, 30)}`)
          accumulatedHeight += height
        } else {
          if (element.tagName === 'DIV') {
            return
          }

          // This should always be round.
          const nbTextLines = (height - margins) / 24
          const textSpace = getSpaceLeft()
          const nbFittingLines = Math.floor(textSpace / 24)

          let countedTextSpace = 0

          // Last lines will need to fit margin as well so it will go next page.
          if (nbTextLines === nbFittingLines) {
            countedTextSpace = (nbTextLines - 1) * 24
          } else {
            countedTextSpace = nbFittingLines * 24
          }

          // console.log(nbTextLines, nbFittingLines, textSpace, countedTextSpace, accumulatedHeight)

          accumulatedHeight += countedTextSpace
          addBreakPoint(`${element.tagName} - ${element.innerText.slice(0, 30)}`)
          accumulatedHeight += height - countedTextSpace
        }
      }
    }

    this.$nextTick(async () => {
      const imagesLoading = Array.from(document.getElementsByTagName('img')).map((img) => {
        if (img.complete) {
          return true
        } else {
          return new Promise((resolve) => {
            img.onload = function () {
              resolve()
            }

            img.onerror = function () {
              resolve()
            }
          })
        }
      })

      await Promise.all([...imagesLoading, document.fonts.ready])

      const contentEl = document.getElementById(this.contentId)
      traverseElements(contentEl)

      const nbPages = Math.ceil(accumulatedHeight / (pageHeight))

      const nbTopPages = Math.ceil(document.getElementById('toc').offsetHeight / (pageHeight + marginHeight)) + 1

      this.topPos = (nbTopPages * 263)

      this.finalLine = `calc(${accumulatedHeight + (nbPages * marginHeight)}px + ${(nbTopPages * 263)}mm)`

      this.debugLines = debugLines.map((line, i) => {
        return {
          top: `calc(${line.top + (i * marginHeight)}px + ${(nbTopPages * 263)}mm)`,
          initialSpaceLeft: line.initialSpaceLeft,
          accumulatedHeight: line.top,
          color: line.borderColor,
          borderColor: line.borderColor,
          from: line.from
        }
      })

      for (let page = 0; page < nbPages; page++) {
        const topPos = (nbTopPages * 263) + (255 + (page * 263))

        this.pageCounters.push({
          text: `${page + 1} / ${nbPages}`,
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
  width: 150px;
  /* background-color: blueviolet; */
  position: absolute;
}

.margin-sizer {
  /* min-height: 297mm;
  height: 297mm; */
  min-height: 8.5mm;
  height: 8.5mm;
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

 .debug-line {
  width: 400px;
  height: 1px;
  position: absolute;
  border: 1px solid;
 }

 .final-line {
  border-color: red;
  color: red
 }
</style>
