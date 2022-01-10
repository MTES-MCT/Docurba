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
        <v-tooltip right>
          <template #activator="{on}">
            <div class="d-block text-truncate" v-on="on" @click="openSection(item)">
              {{ item.titre }}
            </div>
          </template>
          <span>{{ item.titre }}</span>
        </v-tooltip>
      </template>
      <template #append="{item}">
        <v-btn small icon @click="addSectionTo(item)">
          <v-icon>{{ icons.mdiPlus }}</v-icon>
        </v-btn>
      </template>
    </v-treeview>
  </v-row>
</template>
<script>
import { mdiPlus } from '@mdi/js'
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
        mdiPlus
      }
    }
  },
  computed: {
    PACroots () {
      if (!this.contentSearch.length) {
        const roots = this.PAC.filter(section => !section.parent).sort((sa, sb) => {
          return sa.ordre - sb.ordre
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
    addSectionTo (section) {
      console.log(section)
      // const newSection = {

      // }

      // this.emit('add', )
    }
  }
}
</script>
