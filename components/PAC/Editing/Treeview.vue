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
        selection-type="independent"
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
                {{ item.titre || '[Titre Manquant]' }}
              </div>
            </template>
            <span>{{ item.titre || '[Titre Manquant]' }}</span>
          </v-tooltip>
        </template>
        <template #append="{item}">
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
            @click.stop="addSectionTo(item)"
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
                <v-card-title>Supprimer {{ item.titre }}</v-card-title>
                <v-card-text>
                  Etes vous sur de vouloir supprimer cette section ? Attention, les sous-sections seront elles aussi suprimées.
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn depressed tile color="primary" @click="removeItem(item, dialog)">
                    Supprimer
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

// function getDepth (path) {
//   // console.log(path)
//   return (path.replace(/\/intro$/, '').match(/\//g) || []).length
// }

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
      overedItem: ''
    }
  },
  computed: {
    selectedSections: {
      get () {
        return this.value.map(s => s)
      },
      set (newSelection) {
        const selection = uniq(this.value.concat(newSelection))

        // For each added section we add its parent to the selection.
        this.PAC.forEach((section) => {
          if (section.children) {
            const selectedChildren = newSelection.find((s) => {
              const path = section.path.replace(/\/intro$/, '')
              return s !== section.path && s.includes(path)
            })

            if (selectedChildren) {
              selection.push(section.path)
            }
          }
        })

        this.$emit('input', selection)
      }
    },
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
  methods: {
    openSection (section) {
      this.$emit('open', section)
    },
    addSectionTo (parentSection) {
      // if (open) {
      // $event.stopPropagation()
      // }

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
