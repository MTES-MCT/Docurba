<template>
  <div class="page-container text-justify">
    <PACPDFSectionTemplate
      v-for="root in pacData"
      :key="root.path"
      ref="rootsEl"
      :section="root"
      class="print-root"
    />
  </div>
</template>

<script>

export default {
  props: {
    pacData: {
      type: Array,
      required: true
    }
  }
}
</script>

<style scoped>
.page-container {
  page-break-inside: avoid;
}

.print-root {
   /* page-break-after: always; */
   page-break-inside: avoid;
 }
</style>
