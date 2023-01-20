<template>
  <v-row>
    <v-col cols="12">
      <v-treeview
        ref="tree"
        v-model="selectedSections"
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
      >
        <template #label="{item}">
          <v-tooltip right nudge-right="35">
            <template #activator="{on}">
              <div
                class="d-block text-truncate"
                v-on="on"
                @click="openSection(item)"
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
</template>
<script>
import { mdiPlus, mdiDelete, mdiChevronLeft, mdiChevronRight, mdiChevronUp, mdiChevronDown } from '@mdi/js'

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
  computed: {
    selectedSections: {
      get () {
        return this.value.map(s => s)
      },
      set (newSelection) {
        console.log(newSelection)
      }
    }
  },
  mounted () {
    this.fetchSections()
  },
  methods: {
    async fetchSections (table, match) {
      // const { data: sections } = await this.$supabase.from(table).select('*').match(match)

      const { data: sections } = await axios({
        method: 'get',
        url: '/api/trames/regions/74'
      })

      this.sections = sections
    }
  }
}
</script>
