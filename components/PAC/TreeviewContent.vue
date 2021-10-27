<template>
  <v-row>
    <v-col cols="4">
      <client-only>
        <v-row>
          <v-col v-show="editable" cols="12">
            <v-progress-linear height="10" rounded :value="progressValue" />
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
              v-if="!item.children && editable"
              v-model="item.checked"
              class="ml-1 mb-2"
              dense
              hide-details
              :disabled="!item.body.children.length"
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
      <PACContentSection v-for="(root) in PACroots" :key="root.path" :sections="[root]" />
    </v-col>
  </v-row>
</template>

<script>
// import { groupBy } from 'lodash'

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
    const PAC = this.pacData.map(section => Object.assign({ checked: false }, section))

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
    progressValue () {
      const checkedItems = this.PAC.filter(item => item.checked).length

      console.log('checkedItems', checkedItems, this.PAC.length, Math.round(checkedItems / this.PAC.length) * 100)

      return Math.round((checkedItems / this.PAC.length) * 100)
    },
    PACroots () {
      return this.PAC.filter(section => !section.parent).sort((sa, sb) => {
        return sa.ordre - sb.ordre
      })
    }
    // groupedRoots () {
    //   const roots = this.PAC.filter(section => !section.parent)
    //   return groupBy(roots, r => r.dir)
    // }
  },
  methods: {
    scrollTo (item) {
      // console.log(item, item.slug, slugify(item.titre, { lower: true }))
      const targetEl = item.body.children.find(el => el.tag.indexOf('h') === 0)
      const targetId = targetEl ? targetEl.props.id : ''
      if (targetId) {
        if (item.children) {
          // console.log('scroll to', item, target)
          this.$vuetify.goTo(`#${targetId}`)
        } else {
          this.$vuetify.goTo(`#panel-${targetId}`)
        }
      }
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
