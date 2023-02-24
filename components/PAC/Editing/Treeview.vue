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
        :value="selectedSections"
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
        @input="updateSelection"
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
import { uniq } from 'lodash'
import pacEditing from '@/mixins/pacEditing.js'

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
      removedPath: '',
      selectedSections: this.value.map(s => s),
      treeSelection: [],
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
    // selectedSections: {
    //   get () {
    //     return this.value.map(s => s)
    //   },
    //   set (newSelection) {
    //     let selection = uniq(this.value.concat(newSelection))

    //     if (selection.length > this.value.length || newSelection.length < this.value.length) {
    //       if ((this.value.length - newSelection.length) === 1) {
    //         if (!this.removedPath && selection.length <= this.value.length) {
    //           const removedSection = this.value.find(s => !newSelection.includes(s))
    //           if (removedSection) {
    //             this.removedPath = removedSection.replace(/\/intro$/, '')
    //           }
    //         }

    //         if (this.removedPath) {
    //           selection = selection.filter((section) => {
    //             return !section.includes(this.removedPath)
    //           })
    //         }

    //         this.removedPath = ''
    //       }

    //       this.addParentsToSelection(selection)
    //       this.$emit('input', uniq(selection))
    //     }
    //   }
    // },
    PACroots () {
      const roots = this.PAC.filter(section => section.depth === 2).sort((sa, sb) => {
        return (sa.ordre ?? 100) - (sb.ordre ?? 100)
      })

      return roots
    }
  },
  mounted () {
    this.$nextTick(() => {
      this.treeSelection = Array.from(this.$refs.tree.selectedCache)
    })
  },
  methods: {
    openSection (section) {
      this.$emit('open', section)
    },
    addParentsToSelection (selection) {
      this.PAC.forEach((section) => {
        if (section.children) {
          const selectedChildren = selection.find((s) => {
            const path = section.path.replace(/\/intro$/, '')
            return s !== section.path && s.includes(path)
          })

          if (selectedChildren) {
            selection.push(section.path)
          }
        }
      })
    },
    updateSelection (newSelection) {
      // console.log(newSelection.length, this.treeSelection.length)

      if (newSelection.length < this.treeSelection.length) {
        // if something was removed
        let removedPath = this.treeSelection.find(path => !newSelection.includes(path))
        if (removedPath) {
          removedPath = removedPath.replace(/\/intro$/, '')

          // also remove all children
          const selection = this.selectedSections.filter((path) => {
            return !path.includes(removedPath)
          })
          this.emitSelectionUpdate(selection)
        }
      } else if (newSelection.length > this.treeSelection.length) {
        // something was added
        const selection = uniq(this.selectedSections.concat(newSelection))
        this.addParentsToSelection(selection)
        this.emitSelectionUpdate(selection)
      }

      this.treeSelection = newSelection.map(s => s)
    },
    emitSelectionUpdate (selection) {
      // console.log('update selection', selection.length)
      this.$emit('input', selection)
      this.selectedSections = selection
    },
    addSectionTo (parentSection) {
      this.addNewSection(parentSection)
    },
    selectItem (item) {
      this.overedItem = item.path
    },
    removeItem (item, dialog) {
      this.deleteSection(Object.assign({
        path: item.path
      }, this.tableKey))

      this.removedPath = item.path.replace(/\/intro$/, '')

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
