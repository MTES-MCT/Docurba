<template>
  <div ref="pdfTemplate">
    <PACSectionsPDFTemplateSection v-for="root in PACroots" :key="root.path" :section="root" />
  </div>
</template>

<script>
import pacContent from '@/mixins/pacContent.js'

export default {
  mixins: [pacContent],
  computed: {
    PACroots () {
      const roots = this.PAC.filter(section => section.depth === 2).sort((sa, sb) => {
        return sa.ordre - sb.ordre
      })

      return roots
    }
  }
}
</script>
