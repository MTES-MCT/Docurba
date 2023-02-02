<template>
  <v-row v-if="sections.length">
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
              <div
                class="d-block text-truncate"
                v-on="on"
                @click="$emit('open', item)"
                @mouseenter="overedItem = item.path"
              >
                {{ item.name || '[Titre Manquant]' }}
              </div>
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
            :parent="item "
          />
          <PACEditingGitRemoveSectionDialog
            :show-activator="overedItem === item.path && (item.dept || item.project_id || item.region)"
            :section="item "
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
    async fetchSections (table, match) {
      const { data: sections } = await axios({
        method: 'get',
        url: '/api/trames/tree/test' // TODO: change test by the actual ref: dept, projectId or regionCode
      })

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
    }
  }
}
</script>
