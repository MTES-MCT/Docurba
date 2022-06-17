<template>
  <v-container>
    <v-row>
      <v-col>
        <v-treeview
          :items="PACroots"
          open-all
          item-text="titre"
          item-key="path"
          expand-icon=""
        >
          <template #label="{item}">
            <a :href="`#${slugify(item.path.replace(/\//g, '_'))}`">
              {{ item.titre }}
            </a>
          </template>
          <template #append="{item}">
            <a :href="`#${slugify(item.path.replace(/\//g, '_'))}`" class="d-flex">
              <v-spacer />
              {{ getPage(item) }}
            </a>
          </template>
        </v-treeview>
      </v-col>
    </v-row>
    <div ref="content" class="content-sizer" />
    <div ref="page" class="page-sizer" />
  </v-container>
</template>

<script>
import slugify from 'slugify'
import pacContent from '@/mixins/pacContent.js'

export default {
  mixins: [pacContent],
  computed: {
    PACroots () {
      const roots = this.PAC.filter((section) => {
        return section.depth === 2
      })

      return roots
    },
    contentHeight () {
      return this.$refs.content.offsetHeight
    },
    nbPages () {
      const contentEl = document.getElementById('pac-content-pdf')
      const nbPages = (contentEl.offsetHeight / this.contentHeight) + this.PACroots.length

      return nbPages
    },
    topPosition () {
      const elRect = this.$el.getBoundingClientRect()
      const topPosition = elRect.bottom
      return topPosition
    }
  },
  methods: {
    slugify (str) {
      return slugify(str)
    },
    getPage (item) {
      // const contentHeight = this.$refs.content.offsetHeight
      // const nbPages = (this.$el.offsetHeight / contentHeight) + this.PACroots.length

      const itemEl = document.getElementById(slugify(item.path.replace(/\//g, '_')))

      if (itemEl) {
        const itemRect = itemEl.getBoundingClientRect()
        const top = itemRect.top - this.topPosition

        const rootsPositions = this.PACroots.map((r) => {
          const rootEl = document.getElementById(slugify(r.path.replace(/\//g, '_')))
          const rootRect = rootEl.getBoundingClientRect()
          return rootRect.top - this.topPosition
        })

        const nbRootsBefore = rootsPositions.filter((rootTop) => {
          return rootTop <= top
        }).length - 1

        return Math.ceil(top / this.contentHeight) + nbRootsBefore
      } else { return '' }

      // const pageHeight = this.$refs.page.offsetHeight

      // const nbTopPage = Math.ceil(topPosition / this.contentHeight)
    }
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
</style>
