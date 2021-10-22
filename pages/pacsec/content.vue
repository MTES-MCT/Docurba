<template>
  <v-row>
    <v-col cols="4">
      <client-only>
        <v-treeview class="sticky-tree mt-4" style="top: 80px" hoverable :items="PACroots" item-text="titre" />
      </client-only>
    </v-col>
    <v-col cols="8">
      <PACContentSection v-for="(root, slug) in groupedRoots" :key="slug" :sections="root" />
    </v-col>
  </v-row>
</template>

<script>
import { groupBy } from 'lodash'

function getDepth (path) {
  return (path.match(/\//g) || []).length
}

export default {
  async asyncData ({ $content }) {
    const PAC = await $content('PAC', {
      deep: true
    }).fetch()

    PAC.forEach((section) => {
      section.depth = getDepth(section.path)

      const parent = PAC.find((p) => {
        const pDepth = p.depth || getDepth(p.path)

        return p !== section &&
          p.slug === 'intro' &&
          section.dir.includes(p.dir) &&
          (section.slug === 'intro' ? pDepth + 1 : pDepth) === section.depth
      })

      if (parent) {
        section.parent = parent

        if (parent.children) {
          parent.children.push(section)
        } else {
          parent.children = [section]
        }
      }
    })

    PAC.forEach((section) => {
      if (section.children) {
        section.children.sort((sa, sb) => {
          return sa.ordre - sb.ordre
        })
      }
    })

    const PACroots = PAC.filter(section => !section.parent)
    const groupedRoots = groupBy(PACroots, r => r.dir)

    return {
      PAC,
      PACroots,
      groupedRoots
    }
  },
  data () {
    return {}
  },
  computed: {
    // PACroots () {
    //   return this.PAC.filter(section => !section.parent)
    // },
    // groupedRoots () {
    //   const roots = this.PAC.filter(section => !section.parent)

    //   return groupBy(roots, r => r.dir)
    // }
  }
}
</script>

<style scoped>
.sticky-tree {
  position: sticky;
  overflow: scroll;
  max-height: 80vh;
}
</style>
