<template>
  <div>
    <nuxt-content v-if="intro" :document="intro" />
    <template v-for="(section, i) in otherSections">
      <div :key="i" class="mt-4">
        <nuxt-content :document="section" />
      </div>
    </template>
    <PACContentSection v-if="intro.children" :sections="intro.children" />
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
    intro () {
      return this.sections.find(s => s.slug === 'intro')
    },
    otherSections () {
      return this.sections.filter(s => s.slug !== 'intro')
    }
  }
}
</script>
