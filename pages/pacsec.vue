<template>
  <v-container>
    <v-tabs v-model="activeTab" show-arrows>
      <v-tab
        v-for="tab in tabs"
        :key="tab"
        :to="`#${tab}`"
      >
        {{ tab }}
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="activeTab">
      <v-tab-item id="PAC sec">
        <PACContentSection v-for="(root, slug) in PACroots" :key="slug" :sections="root" />
      </v-tab-item>
      <!-- <v-tab-item v-for="(section, i) in PAC" id="">
        <template v-for="(item, i) in section">
          <div :key="i" class="mt-4">
            <template v-if="item.intro">
              <nuxt-content :document="item.intro" />
            </template>
            <v-expansion-panels v-if="item.sections.length" class="pa-4">
              <v-expansion-panel
                v-for="(section) in item.sections"
                :key="section.slug"
              >
                <v-expansion-panel-header>
                  <v-row>
                    <v-col cols="12">
                      <h3 class="text-h3">
                        {{ section.title }}
                      </h3>
                    </v-col>
                    <v-col cols="8">
                      <p>
                        {{ section.description }}
                      </p>
                    </v-col>
                  </v-row>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <nuxt-content :document="section" />
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
          </div>
        </template>
      </v-tab-item> -->
      <v-tab-item id="Jeux de données">
        <DataSourcesList :region="currentRegion" />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
import { groupBy } from 'lodash'

function getDepth (dir) {
  return (dir.match(/\//g) || []).length
}

export default {
  name: 'PACsec',
  async asyncData ({ $content }) {
    const PAC = await $content('PAC', {
      deep: true
    }).fetch()

    PAC.forEach((section) => {
      section.depth = getDepth(section.dir)

      const parent = PAC.find((p) => {
        const pDepth = p.depth || getDepth(section.dir)

        return p.slug === 'intro' &&
          section.dir.includes(p.dir) &&
          (pDepth + 1) === section.depth
      })

      if (parent) {
        section.parent = parent

        if (parent.children) {
          parent.children.push(section)
        } else {
          parent.children = [section]
        }
      }
    })

    return {
      PAC
    }
  },
  data () {
    return {
      tabs: [
        'PAC sec',
        'Jeux de données'
      ],
      activeTab: 'Jeux de données'
    }
  },
  computed: {
    PACroots () {
      const roots = this.PAC.filter(section => !section.parent)

      return groupBy(roots, r => r.dir)
    },
    currentRegion () {
      return this.$route.query.region
    }
  },
  methods: {
  //   getOrder (content) {
  //     return content ? (content.ordre || 100) : 100
  //   },
  //   sortContent (a, b) {
  //     return this.getOrder(a) - this.getOrder(b)
  //   },
  //   parsePacContent (contentRoot) {
  //     let sections = {}

    //     contentRoot.forEach((content) => {
    //       const contentKey = `${content.dir}-${content.depth}`

    //       if (!sections[contentKey]) {
    //         sections[contentKey] = { sections: [] }
    //       }

    //       if (content.slug === 'intro') {
    //         sections[contentKey].intro = content
    //       } else {
    //         sections[contentKey].sections.push(content)
    //       }
    //     })

    //     sections = Object.values(sections)

    //     sections.forEach((item) => {
    //       item.sections.sort((a, b) => {
    //         return this.sortContent(a, b)
    //       })
    //     })

  //     return sections.sort((a, b) => {
  //       return this.sortContent(a.intro, b.intro)
  //     })
  //   }
  }
}
</script>
