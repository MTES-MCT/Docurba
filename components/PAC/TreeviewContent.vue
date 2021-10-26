<template>
  <v-row>
    <v-col cols="4">
      <client-only>
        <v-row>
          <v-col v-show="editable" cols="12">
            <v-progress-linear height="10" rounded />
          </v-col>
          <v-col v-show="!editable" cols="12">
            <div class="text-caption text-center">
              Ce PAC n'est pas un document officiel.
            </div>
          </v-col>
        </v-row>
        <v-treeview
          class="sticky-tree"
          style="top: 80px"
          hoverable
          open-on-click
          :items="PACroots"
          item-text="titre"
        >
          <template #label="{item}">
            <!-- <v-row v-if="!item.children" align="center"> -->
            <!-- <v-col cols="auto"> -->
            <v-checkbox
              v-if="!item.children"
              class="ml-1 mb-2"
              :value="item.checked"
              dense
              hide-details
            >
              <template #label>
                <div @click.prevent.stop="scrollTo(item)">
                  {{ item.titre }}
                </div>
              </template>
            </v-checkbox>
            <!-- </v-col> -->
            <!-- </v-row> -->
            <div v-else @click="scrollTo(item)">
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
    },
    editable: {
      type: Boolean,
      default: false
    }
  },
  data () {
    const PAC = this.pacData.map(section => Object.assign({}, section))

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
