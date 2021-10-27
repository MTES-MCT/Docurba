<template>
  <div class="mt-4">
    <div v-for="(section, i) in sortedSections" :key="i">
      <template v-if="section.children || section.slug === 'intro'">
        <nuxt-content :document="section" />
        <PACContentSection v-if="section.children" :sections="section.children" />
      </template>
      <template v-else>
        <v-expansion-panels :id="`panel-${getFirstId(section)}`" flat>
          <v-expansion-panel>
            <v-expansion-panel-header>
              {{ section.titre }}
            </v-expansion-panel-header>
            <v-expansion-panel-content eager>
              <nuxt-content :document="section" />
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    sections: {
      type: Array,
      required: true
    }
  },
  computed: {
    sortedSections () {
      return this.sections.map(s => s).sort((sa, sb) => {
        return sa.ordre - sb.ordre
      })
    }
  },
  methods: {
    getFirstId (section) {
      const targetEl = section.body.children.find(el => el.tag.indexOf('h') === 0)
      const targetId = targetEl ? targetEl.props.id : ''

      return targetId
    }
  }
}
</script>
