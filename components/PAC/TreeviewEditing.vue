<template>
  <v-row
    class="sticky-tree"
    style="top: 128px"
  >
    <v-col cols="12" class="d-flex align-center pr-0">
      <v-text-field v-model="contentSearch" filled hide-details label="Rechercher" />
      <v-btn icon class="mx-1" @click="$emit('collapse')">
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
                @mouseenter="selecItem(item)"
              >
                {{ item.titre }}
              </div>
            </template>
            <span>{{ item.titre }}</span>
          </v-tooltip>
        </template>
        <template #append="{item, open}">
          <v-btn v-show="overedItem === item.path && item.depth > 2" small icon @click.stop="changeItemOrder(item, -1)">
            <v-icon>{{ icons.mdiChevronUp }}</v-icon>
          </v-btn>
          <v-btn v-show="overedItem === item.path && item.depth > 2" small icon @click.stop="changeItemOrder(item, 1)">
            <v-icon>{{ icons.mdiChevronDown }}</v-icon>
          </v-btn>
          <v-btn v-show="overedItem === item.path" small icon @click="addSectionTo(item, open, $event)">
            <v-icon>{{ icons.mdiPlus }}</v-icon>
          </v-btn>
          <v-dialog
            width="500"
          >
            <template #activator="{on}">
              <v-btn v-show="overedItem === item.path && (item.dept || item.project_id)" small icon v-on="on">
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
                  <v-btn color="primary" @click="removeItem(item, dialog)">
                    Suprimer
                  </v-btn>
                  <v-btn color="primary" outlined @click="dialog.value = false">
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
import { v4 as uuidv4 } from 'uuid'
import { uniq } from 'lodash'
import pacContent from '@/mixins/pacContent.js'

function getDepth (path) {
  // console.log(path)
  return (path.replace(/\/intro$/, '').match(/\//g) || []).length
}

export default {
  mixins: [pacContent],
  props: {
    value: {
      type: Array,
      default () { return [] }
    },
    collapsed: {
      type: Boolean,
      default: false
    },
    // This is used for hierarchie update
    table: {
      type: String,
      default () {
        return this.projectId ? 'pac_sections_project' : 'pac_sections_dept'
      }
    },
    projectId: {
      type: String,
      default: ''
    },
    dept: {
      type: String,
      default: ''
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
          (section.path || section).includes(path) &&
          depth < getDepth(section.path || section)
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
    addSectionTo (section, open, $event) {
      if (open) {
        $event.stopPropagation()
      }

      const dir = section.slug === 'intro' ? section.dir : section.path

      const newSection = {
        slug: 'new-section',
        dir,
        titre: 'Nouvelle section',
        path: `${dir}/${Date.now()}`,
        text: 'Nouvelle section'
      }

      this.$emit('add', newSection)
    },
    selecItem (item) {
      this.overedItem = item.path
    },
    removeItem (item, dialog) {
      this.$emit('remove', item)
      dialog.value = false
    },
    async changeItemOrder (item, change) {
      const parent = this.PAC.find((p) => {
        return p !== item &&
          item.dir.includes(p.path.replace(/\/intro$/, '')) &&
            p.depth + 1 === item.depth
      })

      const newIndex = item.ordre + change

      if (newIndex >= 0 && newIndex < parent.children.length) {
        [parent.children[item.ordre], parent.children[newIndex]] = [parent.children[newIndex], parent.children[item.ordre]]

        if (this.table) {
          // parent.children.forEach(async (s, i) => {
          //   await this.$supabase.from(this.table).update({ ordre: i }).eq('id', s.id)
          // })

          const updatedSections = parent.children.map((s, i) => {
            const section = {
              id: s.id || uuidv4(),
              path: s.path,
              dir: s.dir,
              ordre: i
            }

            if (this.projectId) {
              section.project_id = this.projectId
            } else {
              section.dept = this.dept
            }

            return section
          })

          await this.$supabase.from(this.table).upsert(updatedSections)
        }
      }
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
