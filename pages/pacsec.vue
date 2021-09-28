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
      <v-tab-item id="Cadre juridique">
        <template v-for="(item, i) in CadreJuridiqueContent">
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
      </v-tab-item>
      <v-tab-item id="Documents supra-territoriaux">
        <v-expansion-panels class="pa-4">
          <v-expansion-panel
            v-for="(item) in DocSupra"
            :key="item.slug"
          >
            <v-expansion-panel-header>
              <v-row>
                <v-col cols="12">
                  <h3 class="text-h3">
                    {{ item.title }}
                  </h3>
                </v-col>
                <v-col cols="8">
                  <p>
                    {{ item.description }}
                  </p>
                </v-col>
              </v-row>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <nuxt-content :document="item" />
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-tab-item>
      <v-tab-item id="Jeux de données">
        <DataSourcesList />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>

export default {
  async asyncData ({ $content }) {
    const CadreJuridique = await $content('CadreJuridique', {
      deep: true
    }).fetch()
    const DocSupra = await $content('DocumentsSupra-territoriaux').fetch()

    return {
      CadreJuridique,
      DocSupra
    }
  },
  data () {
    return {
      tabs: [
        'Cadre juridique',
        'Documents supra-territoriaux',
        // 'Politiques publiques spécifiques',
        // 'Servitudes d’utilité publique',
        'Jeux de données'
      ],
      activeTab: 'Jeux de données'
    }
  },
  computed: {
    CadreJuridiqueContent () {
      return this.parsePacContent(this.CadreJuridique)
    }
  },
  methods: {
    getOrder () {
      return 1
    },
    parsePacContent (contentRoot) {
      const sections = {}

      contentRoot.forEach((content) => {
        const contentKey = `${content.dir}-${content.depth}`

        if (!sections[contentKey]) {
          sections[contentKey] = { sections: [] }
        }

        if (content.slug === 'intro') {
          sections[contentKey].intro = content
        } else {
          sections[contentKey].sections.push(content)
        }
      })

      return Object.values(sections)
    }
  }
}
</script>
