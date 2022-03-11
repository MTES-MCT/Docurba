<template>
  <div class="root-container text-justify">
    <PACSectionsPDFTemplateSection
      v-for="root in PACroots"
      :key="root.path"
      :section="root"
      class="print-root"
    />
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

<style scoped>
 /* .print-root {
   page-break-after: always;
 } */

/* tr {
  page-break-after: always;
} */

 .root-container {
   padding-right: 0mm;
 }
</style>
