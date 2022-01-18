<template>
  <v-row>
    <v-col cols="4">
      <client-only>
        <v-row
          class="sticky-tree"
          style="top: 120px"
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
                  Ce PAC n'est pas un document officiel.
                </div>
              </template>
              <span>Pour obtenir un document spécifique à votre projet vous devez vous connecter et créer un projet.</span>
              <!-- <InputsLoginOrDocs /> -->
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
              <!-- <v-row v-if="!item.children" align="center"> -->
              <!-- <v-col cols="auto"> -->
              <v-tooltip right>
                <template #activator="{on}">
                  <v-checkbox
                    v-if="!item.children && editable"
                    v-model="item.checked"
                    class="ml-1 mb-2 d-block text-truncate"
                    dense
                    hide-details
                    :disabled="!item.body.children.length"
                    @change="$emit('read', item)"
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
                  <!-- </v-col> -->
                  <!-- </v-row> -->
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
    </v-col>
    <v-col cols="8">
      <div v-for="(root) in PACroots" :key="root.path">
        <PACContentSection :sections="[root]" :editable="editable" />
        <v-divider />
      </div>
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
    return {
      contentSearch: ''
    }
  },
  computed: {
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
    },
    progressValue () {
      const checkedItems = this.PAC.filter(item => item.checked).length

      return Math.round((checkedItems / this.PAC.length) * 100)
    },
    PACroots () {
      if (!this.contentSearch.length) {
        const roots = this.PAC.filter(section => section.depth === 2).sort((sa, sb) => {
          return sa.ordre - sb.ordre
        })

        // Temporary filter
        // roots.filter(r => !!r.children).forEach((root) => {
        //   root.children = root.children.filter((c) => {
        //     return (c.children && c.children.length) ||
        //     (c.body && c.body.children && c.body.children.length > 1)
        //   })
        // })

        return roots
      } else {
        return this.filteredPAC
      }
    }
  },
  methods: {
    scrollTo (item) {
      // const targetEl = item.body.children.find(el => {
      //   return el.tag && el.tag.indexOf('h') === 0
      // })

      // const targetId = targetEl ? targetEl.props.id : ''
      const targetId = item.body.children[0].props.id

      if (targetId) {
        try {
          this.$vuetify.goTo(`#${targetId}`)
        } catch (err) {
          this.$vuetify.goTo(`#panel-${targetId}`)
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
  max-height: calc(100vh - 80px);
}
</style>
