<template>
  <v-row
    class="sticky-tree"
    style="top: 120px"
  >
    <v-col cols="12">
      <v-text-field v-model="contentSearch" filled hide-details label="Rechercher" />
    </v-col>
    <v-treeview
      hoverable
      open-on-click
      :items="PACroots"
      item-text="titre"
      class="d-block text-truncate"
      item-key="path"
    >
      <template #label="{item}">
        <v-tooltip right nudge-right="35">
          <template #activator="{on}">
            <div class="d-block text-truncate" v-on="on" @click="openSection(item)" @mouseenter="selecItem(item)">
              {{ item.titre }}
            </div>
          </template>
          <span>{{ item.titre }}</span>
        </v-tooltip>
      </template>
      <template #append="{item, open}">
        <v-btn v-show="overedItem === item.path" small icon @click="addSectionTo(item, open, $event)">
          <v-icon>{{ icons.mdiPlus }}</v-icon>
        </v-btn>
        <v-dialog
          width="500"
        >
          <template #activator="{on}">
            <v-btn v-show="overedItem === item.path && item.dept" small icon v-on="on">
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
  </v-row>
</template>
<script>
import { mdiPlus, mdiDelete } from '@mdi/js'
import pacContent from '@/mixins/pacContent.js'

export default {
  mixins: [pacContent],
  props: {
    minFilter: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      contentSearch: '',
      icons: {
        mdiPlus,
        mdiDelete
      },
      overedItem: ''
    }
  },
  computed: {
    PACroots () {
      if (!this.contentSearch.length) {
        const roots = this.PAC.filter(section => section.depth === 2).sort((sa, sb) => {
          return (sa.ordre || 100) - (sb.ordre || 100)
        })

        return roots
      } else {
        return this.filteredPAC
      }
    },
    filteredPAC () {
      if (this.contentSearch.length) {
        const searchedContent = this.PAC.map((section) => {
          const searchedSection = { searched: section.searched }

          if (!section.searched) {
            const searchedValue = this.contentSearch.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '')
            const searched = section.searchValue.includes(searchedValue)

            searchedSection.searched = searched
          }

          return Object.assign(searchedSection, section)
        })

        return searchedContent.filter(section => section.searched)
      } else { return this.PAC }
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
    }
  }
}
</script>
