<template>
  <div class="print-section">
    <nuxt-content :document="enrichedSection" />
    <PACPDFSectionTemplate v-for="s in section.children" :key="s.path" :section="s" />
  </div>
</template>
<script>
import slugify from 'slugify'

export default {
  props: {
    section: {
      type: Object,
      required: true
    }
  },
  data () {
    const enrichedSection = Object.assign({}, this.section)

    if (enrichedSection.body) {
      const firstChild = enrichedSection.body.children[0]

      if (firstChild) {
        firstChild.props.id = slugify(enrichedSection.path.replace(/\//g, '_'))
      }
    }

    return {
      enrichedSection
    }
  }
}
</script>

<style>
.print-section .nuxt-content p {
  text-align: justify !important;
  overflow-wrap: break-word;
}
</style>
