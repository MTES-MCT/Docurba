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
            @update="fetchSections"
          />
          <PACEditingGitRemoveSectionDialog
            :show-activator="overedItem === item.path && !isSectionReadonly(item)"
            :section="item "
            @update="fetchSections"
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
    value: {
      type: Array,
      default () { return [] }
    },
    // pacData should be a unified array of sections from DB. See if parent is mixing unifiedPac.js
    pacData: {
      type: Array,
      required: true
    },
    readonlyDirs: {
      type: Array,
      default () {
        return []
      }
    },
    table: {
      type: String,
      required: true
    },
    // This should be the section identifiers in the table.
    // For exemple: {project_id: 'XXX'} for table pac_sections_project
    tableKeys: {
      type: Object,
      required: true
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
    // mergeGitWithBD (section) {
    //   const dbSection = this.pacData.find(s => s.path.replace('/', '') === section.path.replace('.md', ''))

    //   if (dbSection) {
    //     console.log(dbSection)
    //   }
    //   // else if (section.type === 'file') {
    //   //   console.log(section.path.replace('.md', ''), this.pacData[0].path)
    //   // }

    //   if (section.children) {
    //     section.children.forEach(s => this.mergeGitWithBD(s))
    //   }
    // },
    async fetchSections () {
      const { data: sections } = await axios({
        method: 'get',
        url: '/api/trames/tree/test' // TODO: change test by the actual ref: dept, projectId or regionCode
      })

      // console.log(this.pacData[0])

      // sections.forEach(section => this.mergeGitWithBD(section))

      this.sections = sections
    },
    async updateSelection (newSelection) {
      let selection = []

      if (newSelection.length < this.treeSelection.length) {
        // if something was removed
        const removedPath = this.treeSelection.find(path => !newSelection.includes(path))
        if (removedPath) {
        // also remove all children
          selection = this.selectedSections.filter((path) => {
            return !path.includes(removedPath)
          })
        }
      } else if (newSelection.length > this.treeSelection.length) {
        // something was added
        selection = uniq(this.selectedSections.concat(newSelection))
        this.addParentsToSelection(selection, this.sections)
      }

      this.selectedSections = selection

      // Update the selection for this project in supabase.
      if (this.selectable && this.tableKeys.project_id) {
      // This make it so we can't save sections as objects in reading mode for comments and checked features.
        await this.$supabase.from('projects').update({
          PAC: selection.map(s => s || s.path)
        }).eq('id', this.tableKeys.project_id)

        this.$notifications.notifyUpdate(this.tableKeys.project_id)
      }

      this.treeSelection = newSelection.map(s => s)
    },
    addParentsToSelection (selection, sections) {
      sections.forEach((section) => {
        if (section.children) {
          this.addParentsToSelection(selection, section.children)

          const selectedChildren = selection.find((s) => {
            return s !== section.path && s.includes(section.path)
          })

          if (selectedChildren) {
            selection.push(section.path)
          }
        }
      })
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
