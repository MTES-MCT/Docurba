<template>
  <v-row v-if="sections.length" class="sticky-tree">
    <v-col cols="12">
      <v-treeview
        ref="tree"
        :value="selectedSections"
        hoverable
        open-on-click
        :selectable="selectable"
        :items="sections"
        item-text="name"
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
              <transition name="fade">
                <div
                  class="d-block text-truncate"
                  v-on="on"
                  @click="$emit('open', item)"
                  @mouseenter="overedItem = item.path"
                >
                  {{ item.name || '[Titre Manquant]' }}
                </div>
              </transition>
            </template>
            <span>{{ item.name || '[Titre Manquant]' }}</span>
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
          <PACEditingGitAddSectionDialog
            :show-activator="overedItem === item.path"
            :parent="item"
            :git-ref="gitRef"
            @added="addSection"
          />
          <PACEditingGitRemoveSectionDialog
            :show-activator="overedItem === item.path && !isSectionReadonly(item)"
            :section="item"
            :git-ref="gitRef"
            @removed="removeSection"
          />
        </template>
      </v-treeview>
    </v-col>
  </v-row>
  <VGlobalLoader v-else />
</template>
<script>
import { mdiDelete, mdiChevronLeft, mdiChevronRight, mdiChevronUp, mdiChevronDown } from '@mdi/js'
import { uniq } from 'lodash'
import axios from 'axios'

export default {
  props: {
    // Value is an array of section paths in string.
    // It represent the selected sections for this project.
    // It's not applicable outside of projects.
    value: {
      type: Array,
      default () { return [] }
    },
    readonlyDirs: {
      type: Array,
      default () {
        return []
      }
    },
    collapsed: {
      type: Boolean,
      default: false
    },
    selectable: {
      type: Boolean,
      default: false
    },
    project: {
      type: Object,
      default () { return {} }
    },
    gitRef: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      contentSearch: '',
      overedItem: '',
      sections: [],
      selectedSections: this.value.map(s => s),
      treeSelection: [],
      icons: {
        mdiDelete,
        mdiChevronLeft,
        mdiChevronRight,
        mdiChevronUp,
        mdiChevronDown
      }
    }
  },
  async mounted () {
    await this.fetchSections()

    // We need to wait for the tree to render so that we can get its internal selected value.
    this.$nextTick(() => {
      this.treeSelection = Array.from(this.$refs.tree.selectedCache)
    })
  },
  methods: {
    async fetchSections () {
      const { data: sections } = await axios({
        method: 'get',
        url: `/api/trames/tree/${this.gitRef}`
      })

      this.sections = sections
    },
    addSection (newSection, parent) {
      parent.children.push(newSection)
      // It's safer to fetch the sections again to avoid sync issues.
      this.fetchSections()
    },
    removeSection (removedSection) {
      function filterSections (children) {
        children.forEach((child) => {
          if (child.children) {
            child.children = filterSections(child.children)
          }
        })

        return children.filter(s => s.path !== removedSection.path)
      }

      this.sections.forEach((section) => {
        if (section.children) {
          section.children = filterSections(section.children)
        }
      })

      this.sections = [...this.sections]
      this.fetchSections()
    },
    async updateSelection (newSelection) {
      // console.log(newSelection, this.treeSelection)

      if (newSelection.length !== this.treeSelection.length) {
        let selection = []
        if (newSelection.length < this.treeSelection.length) {
        // if something was removed
          const removedPaths = this.treeSelection.filter(path => !newSelection.includes(path))
          // console.log(removedPaths.length)
          if (removedPaths.length === 1) {
          // also remove all children
            selection = this.selectedSections.filter((path) => {
              return !path.includes(removedPaths[0])
            })
          } else {
            // console.log('do not save')
            return
          }
        } else if (newSelection.length > this.treeSelection.length) {
        // something was added
          selection = uniq(this.selectedSections.concat(newSelection))
          this.addParentsToSelection(selection, this.sections)
        }

        // console.log('saving')

        this.selectedSections = uniq(selection)
        this.treeSelection = newSelection.map(s => s)

        // Update the selection for this project in supabase.
        if (this.selectable && this.project.id) {
        // This make it so we can't save sections as objects in reading mode for comments and checked features.
          await this.$supabase.from('projects').update({
            PAC: this.selectedSections.map(s => s || s.path)
          }).eq('id', this.project.id)

          this.$notifications.notifyUpdate(this.project.id)
        }
      }
    },
    addParentsToSelection (selection, sections) {
      const selectedParents = []

      sections.forEach((section) => {
        if (section.children) {
          this.addParentsToSelection(selection, section.children)

          const selectedChildren = selection.find((s) => {
            return s !== section.path && s.includes(section.path)
          })

          if (selectedChildren) {
            selectedParents.push(section.path)
          }
        }
      })

      selection.push(...selectedParents)
    },
    isSectionReadonly (section) {
      return !!this.readonlyDirs.find((dir) => {
        return section.path.includes(dir)
      })
    }
  }
}
</script>

<style scoped>
.sticky-tree {
  /* position: sticky; */
  overflow: scroll;
  /* 128 = 80 (from search row ) + 48 (one tree leaf) */
  max-height: calc(100vh - 128px);
}

.fade-enter-active {
  transition: opacity .5s;
}

.fade-enter {
  opacity: 0;
}
</style>
