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

  }
}
</script>
