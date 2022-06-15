<template>
  <div>
    <nuxt-content :document="section" />
    <PACPDFSectionTemplate v-for="s in section.children" :key="s.path" :section="s" />
  </div>
</template>
<script>
export default {
  props: {
    section: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.nuxt-content p {
  text-align: justify !important;
}
</style>
