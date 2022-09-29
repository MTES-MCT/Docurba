<template>
  <v-row>
    <!-- <v-col cols="4">
      <client-only>
        <v-row
          class="sticky-tree"
          style="top: 176px"
        >
          <v-col cols="12">
            <v-text-field v-model="contentSearch" filled hide-details label="Rechercher" />
          </v-col>
          <v-col v-show="editable" cols="12">
            <v-progress-linear height="10" rounded :value="progressValue" />
          </v-col>
          <v-col v-show="!editable" cols="12">
            <v-tooltip right>
              <template #activator="{on}">
                <div class="text-caption text-center" v-on="on">
                  Ce document n'est pas le PAC complet officiel
                </div>
              </template>
              <span>Pour obtenir un document spécifique à votre projet vous devez vous connecter et créer un projet.</span>
            </v-tooltip>
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
                  <v-checkbox
                    v-if="(!item.children || !item.children.length) && editable"
                    v-model="item.checked"
                    class="ml-1 mb-2 d-block text-truncate"
                    dense
                    hide-details
                    :disabled="!item.body.children.length"
                    @change="checkItem(item)"
                  >
                    <template #label>
                      <div
                        class="d-block text-truncate"
                        style="width: calc(33vw - 125px)"
                        v-on="on"
                        @click.prevent.stop="scrollTo(item)"
                      >
                        {{ item.titre }}
                      </div>
                    </template>
                  </v-checkbox>
                  <div
                    v-else
                    class="d-block text-truncate"
                    style="width: 100%"
                    v-on="on"
                    @click="scrollTo(item)"
                  >
                    {{ item.titre }}
                  </div>
                </template>
                <span>{{ item.titre }}</span>
              </v-tooltip>
            </template>
          </v-treeview>
        </v-row>
      </client-only>
    </v-col> -->
    <v-col cols="12">
      <PACContentSection :sections="PACroots" :editable="editable" />
    </v-col>
  </v-row>
</template>

<script>
import pacContent from '@/mixins/pacContent.js'

export default {
  mixins: [pacContent],
  props: {
    editable: {
      type: Boolean,
      default: false
    }
  },
  data () {
    const PACroots = this.parsePAC().filter(section => section.depth === 2).sort((sa, sb) => {
      return sa.ordre - sb.ordre
    })

    PACroots.forEach((root, index) => {
      if (index) {
        this.addCounter(root, [index])
      }
    })

    return {
      contentSearch: '',
      checkedItems: 0,
      PACroots
    }
  },
  computed: {
    // filteredPAC () {
    //   if (this.contentSearch.length) {
    //     const searchedContent = this.PAC.map((section) => {
    //       const searchedSection = { searched: section.searched }

    //       if (!section.searched) {
    //         const searchedValue = this.contentSearch.toLowerCase().normalize('NFD').replace(/[À-ÿ]/gu, '')
    //         const searched = section.searchValue.includes(searchedValue)

    //         searchedSection.searched = searched
    //       }

    //       return Object.assign(searchedSection, section)
    //     })

    //     return searchedContent.filter(section => section.searched)
    //   } else { return this.PAC }
    // },
    // progressValue () {
    //   return Math.round((this.checkedItems / this.PAC.length) * 100)
    // }
    // PACroots () {
    //   if (!this.contentSearch.length) {
    //     const roots = this.PAC.filter(section => section.depth === 2).sort((sa, sb) => {
    //       return sa.ordre - sb.ordre
    //     })

    //     return roots
    //   } else {
    //     return this.filteredPAC
    //   }
    // }
  },
  mounted () {
    this.checkedItems = this.PAC.filter(item => item.checked).length

    // this.PACroots.forEach((root, index) => {
    //   this.addCounter(root, [index + 1])
    // })
  },
  methods: {
    checkItem (section) {
      if (section.checked) {
        this.checkedItems += 1
      } else { this.checkedItems -= 1 }

      this.$emit('read', section)
    },
    scrollTo (item) {
      if (item.body.children && item.body.children.length) {
        if ((item.children && item.children.length) || item.slug === 'intro') {
          this.$vuetify.goTo(`#${item.path.replaceAll(/[^A-Za-z0-9]/g, '__')}`)
        } else {
          this.$vuetify.goTo(`#panel__${item.path.replaceAll(/[^A-Za-z0-9]/g, '__')}`)
        }
      }
    }
  }
}
</script>

<style scoped>
.sticky-tree {
  position: sticky;
  overflow: scroll;
  /* 128 = 80 (from search row ) + 48 (one tree leaf) */
  max-height: calc(100vh - 176px);
}
</style>
