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
function getDepth (path) {
  return (path.match(/\//g) || []).length
}

export default {
  props: {
    pacData: {
      type: Array,
      required: true
    },
    editable: {
      type: Boolean,
      default: false
    }
  },
  data () {
    const PAC = this.pacData.map((section) => {
      const serachText = `${section.titre} ${section.slug}`.toLowerCase()

      return Object.assign({
        checked: false,
        searchValue: serachText.normalize('NFD').replace(/\p{Diacritic}/gu, '')
      }, section)
    })

    PAC.forEach((section) => {
      section.depth = getDepth(section.path)

      const parent = PAC.find((p) => {
        const pDepth = p.depth || getDepth(p.path)

        return p !== section &&
          p.slug === 'intro' &&
          section.dir.includes(p.dir) &&
          (section.slug === 'intro' ? pDepth + 1 : pDepth) === section.depth
      })

      if (parent) {
        section.parent = parent

        if (parent.children) {
          if (!parent.children.includes(section)) {
            parent.children.push(section)
          }
        } else {
          parent.children = [section]
        }
      }

      return section
    })

    PAC.forEach((section) => {
      if (section.children) {
        // Temporary filter
        section.children = section.children.filter((c) => {
          return (c.children && c.children.length) ||
            (c.body && c.body.children && c.body.children.length > 1)
        })

        section.children.sort((sa, sb) => {
          return sa.ordre - sb.ordre
        })
      }
    })

    return {
      PAC,
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

          // console.log(searchedSection.searched, section.searchValue)

          // if (searchedSection.searched && section.parent) {
          //   section.parent.searched = true
          // }

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
        const roots = this.PAC.filter(section => !section.parent).sort((sa, sb) => {
          return sa.ordre - sb.ordre
        })

        // Temporary filter
        roots.forEach((root) => {
          root.children = root.children.filter((c) => {
            return (c.children && c.children.length) ||
            (c.body && c.body.children && c.body.children.length > 1)
          })
        })

        return roots
      } else {
        return this.filteredPAC
      }
    }
  },
  methods: {
    scrollTo (item) {
      const targetEl = item.body.children.find(el => el.tag.indexOf('h') === 0)
      const targetId = targetEl ? targetEl.props.id : ''
      if (targetId) {
        if (item.children) {
          this.$vuetify.goTo(`#${targetId}`)
        } else {
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
