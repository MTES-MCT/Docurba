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
                <v-card-title>Supprimer {{ item.name }}</v-card-title>
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
  <VGlobalLoader v-else />
</template>
<script>
import { mdiPlus, mdiDelete, mdiChevronLeft, mdiChevronRight, mdiChevronUp, mdiChevronDown } from '@mdi/js'
import { uniq } from 'lodash'
import axios from 'axios'

export default {
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
      overedItem: '',
      sections: [],
      selectedSections: this.value.map(s => s),
      treeSelection: [],
      icons: {
        mdiPlus,
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
        url: '/api/trames/regions/74'
      })

      this.sections = sections
    },
    updateSelection (newSelection) {
      if (newSelection.length < this.treeSelection.length) {
        // if something was removed
        const removedPath = this.treeSelection.find(path => !newSelection.includes(path))
        if (removedPath) {
        // also remove all children
          const selection = this.selectedSections.filter((path) => {
            return !path.includes(removedPath)
          })
          this.emitSelectionUpdate(selection)
        }
      } else if (newSelection.length > this.treeSelection.length) {
        // something was added
        const selection = uniq(this.selectedSections.concat(newSelection))
        this.addParentsToSelection(selection, this.sections)
        this.emitSelectionUpdate(selection)
      }

      this.treeSelection = newSelection.map(s => s)
    },
    emitSelectionUpdate (selection) {
      this.$emit('input', selection)
      this.selectedSections = selection
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
