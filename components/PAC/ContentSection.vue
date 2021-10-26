<template>
  <div class="mt-4">
    <div v-for="(section, i) in sortedSections" :key="i">
      <nuxt-content :document="section" />
      <PACContentSection v-if="section.children" :sections="section.children" />
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
  }
}
</script>
