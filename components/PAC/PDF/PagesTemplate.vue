<template>
  <div class="root-container text-justify">
    <PACPDFSectionTemplate
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
 .print-root {
   /* page-break-after: always; */
   page-break-inside: avoid;
 }

/* tr {
  page-break-after: always;
} */

 .root-container {
   page-break-inside: avoid;
 }
</style>
