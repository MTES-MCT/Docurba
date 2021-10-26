<template>
  <v-row>
    <v-col cols="4">
      <client-only>
        <v-treeview
          class="sticky-tree mt-4"
          style="top: 80px"
          hoverable
          open-on-click
          :items="PACroots"
          item-text="titre"
        >
          <template #label="{item}">
            <div @click="scrollTo(item)">
              {{ item.titre }}
            </div>
          </template>
        </v-treeview>
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
  props: {
    pacData: {
      type: Array,
      required: true
    }
  },
  data () {
    const PAC = this.pacData.map(section => section)

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
          if (!parent.children.includes(section)) {
            parent.children.push(section)
          }
        } else {
          parent.children = [section]
        }
      }

      return section
    })

    PAC.forEach((section) => {
      if (section.children) {
        section.children.sort((sa, sb) => {
          return sa.ordre - sb.ordre
        })
      }
    })

    return {
      PAC
    }
  },
  computed: {
    PACroots () {
      return this.PAC.filter(section => !section.parent)
    },
    groupedRoots () {
      const roots = this.PAC.filter(section => !section.parent)

      return groupBy(roots, r => r.dir)
    }
  },
  methods: {
    scrollTo (item) {
      // console.log(item, item.slug, slugify(item.titre, { lower: true }))

      const target = item.body.children.find(el => el.tag.indexOf('h') === 0).props.id
      this.$vuetify.goTo(`#${target}`)
    }
  }
}
</script>

<style scoped>
.sticky-tree {
  position: sticky;
  overflow: scroll;
  max-height: calc(100vh - 80px);
}
</style>
