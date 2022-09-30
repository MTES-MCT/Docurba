<template>
  <v-row
    class="sticky-tree"
    style="top: 128px"
  >
    <v-col cols="12" class="d-flex align-center pr-0">
      <v-text-field v-model="contentSearch" filled hide-details label="Rechercher" />
      <v-btn depressed tile icon class="mx-1" @click="$emit('collapse')">
        <v-icon>{{ collapsed ? icons.mdiChevronRight : icons.mdiChevronLeft }}</v-icon>
      </v-btn>
    </v-col>
    <v-col cols="12" class="pa-0" @click="collapsed ? $emit('collapse') : ''">
      <v-treeview
        ref="tree"
        v-model="selectedSections"
        hoverable
        open-on-click
        :selectable="selectable"
        :items="PACroots"
        item-text="titre"
        class="d-block text-truncate"
        item-key="path"
        selected-color="primary"
        :search="contentSearch"
      >
        <template #label="{item}">
          <v-tooltip right nudge-right="35">
            <template #activator="{on}">
              <div
                class="d-block text-truncate"
                :class="colorClass(item)"
                v-on="on"
                @click="openSection(item)"
                @mouseenter="selectItem(item)"
              >
                {{ item.titre }}
              </div>
            </template>
            <span>{{ item.titre }}</span>
          </v-tooltip>
        </template>
        <template #append="{item, open}">
          <v-btn
            v-show="overedItem === item.path && item.depth > 2"
            depressed
            tile
            small
            icon
            @click.stop="changeSectionOrder(item, -1)"
          >
            <v-icon>{{ icons.mdiChevronUp }}</v-icon>
          </v-btn>
          <v-btn
            v-show="overedItem === item.path && item.depth > 2"
            depressed
            tile
            small
            icon
            @click.stop="changeSectionOrder(item, 1)"
          >
            <v-icon>{{ icons.mdiChevronDown }}</v-icon>
          </v-btn>
          <v-btn
            v-show="overedItem === item.path"
            depressed
            tile
            small
            icon
            @click="addSectionTo(item, open, $event)"
          >
            <v-icon>{{ icons.mdiPlus }}</v-icon>
          </v-btn>
          <v-dialog
            width="500"
          >
            <template #activator="{on}">
              <v-btn
                v-show="overedItem === item.path && (item.dept || item.project_id || item.region)"
                depressed
                tile
                small
                icon
                v-on="on"
              >
                <v-icon>{{ icons.mdiDelete }}</v-icon>
              </v-btn>
            </template>
            <template #default="dialog">
              <v-card>
                <v-card-title>Suprimer {{ item.titre }}</v-card-title>
                <v-card-text>
                  Etes vous sur de vouloir suprimer cette section ? Attention, les sous-sections seront elles aussi suprimées.
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn depressed tile color="primary" @click="removeItem(item, dialog)">
                    Suprimer
                  </v-btn>
                  <v-btn depressed tile color="primary" outlined @click="dialog.value = false">
                    Annuler
                  </v-btn>
                </v-card-actions>
              </v-card>
            </template>
          </v-dialog>
        </template>
      </v-treeview>
    </v-col>
  </v-row>
</template>
<script>
import { mdiPlus, mdiDelete, mdiChevronLeft, mdiChevronRight, mdiChevronUp, mdiChevronDown } from '@mdi/js'
// import { v4 as uuidv4 } from 'uuid'
import { uniq } from 'lodash'
import pacEditing from '@/mixins/pacEditing.js'

function getDepth (path) {
  // console.log(path)
  return (path.replace(/\/intro$/, '').match(/\//g) || []).length
}

export default {
  mixins: [pacEditing],
  props: {
    value: {
      type: Array,
      default () { return [] }
    },
    collapsed: {
      type: Boolean,
      default: false
    },
    selectable: {
      type: Boolean,
      default: false
    }
  },
  data () {
    const children = this.value.filter((s) => {
      const path = (s.path || s).replace(/\/intro$/, '')
      const depth = getDepth(path)

      const child = this.value.find((section) => {
        // console.log((section.path || section), path)

        return s !== section &&
          (section.path || section).includes(path + '/') &&
          depth + 1 === getDepth(section.path || section)
      })

      return !child
    })

    return {
      contentSearch: '',
      icons: {
        mdiPlus,
        mdiDelete,
        mdiChevronLeft,
        mdiChevronRight,
        mdiChevronUp,
        mdiChevronDown
      },
      overedItem: '',
      selectedSections: children
    }
  },
  computed: {
    PACroots () {
      // if (!this.contentSearch.length) {
      const roots = this.PAC.filter(section => section.depth === 2).sort((sa, sb) => {
        return (sa.ordre ?? 100) - (sb.ordre ?? 100)
      })

      return roots
      // } else {
      //   return this.filteredPAC
      // }
    }
  },
  watch: {
    selectedSections () {
      // if (!this.contentSearch.length) {
      const selection = []

      this.PAC.forEach((section) => {
        if (section.children) {
          const selectedChildren = this.selectedSections.find((s) => {
            const path = section.path.replace(/\/intro$/, '')
            return s !== section.path && s.includes(path)
          })

          if (selectedChildren) {
            selection.push(section.path)
          }
        }
      })

      this.$emit('input', uniq(selection.concat(this.selectedSections)))
      // }
    }
  },
  methods: {
    openSection (section) {
      this.$emit('open', section)
    },
    addSectionTo (parentSection, open, $event) {
      if (open) {
        $event.stopPropagation()
      }

      this.addNewSection(parentSection)
    },
    selectItem (item) {
      this.overedItem = item.path
    },
    removeItem (item, dialog) {
      this.deleteSection(Object.assign({
        path: item.path
      }, this.tableKey))
      dialog.value = false
    },
    colorClass (section) {
      // textEdited is setup in unifiedPac.js
      if (section.textEdited) {
        if (section.project_id) {
          return 'bf500--text'
        }

        if (section.dept) {
          return 'bf300--text'
        }
      }

      return ''
    }
  }
}
</script>

<style scoped>
.sticky-tree {
  position: sticky;
  overflow: scroll;
  /* 128 = 80 (from search row ) + 48 (one tree leaf) */
  max-height: calc(100vh - 128px);
}
</style>
