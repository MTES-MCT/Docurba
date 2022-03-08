<template>
  <div>
    <nuxt-content :document="section" />
    <PACSectionsPDFTemplateSection v-for="s in section.children" :key="s.path" :section="s" />
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
