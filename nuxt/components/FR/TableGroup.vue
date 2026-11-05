<script>
export default {
  props: {
    cols: {
      default: '',
      type: String,
    },
  },
  computed: {
    elementStyle() {
      const cols = this.cols.split(' ')

      return {
        '--fr-table__cols': cols.map((col) =>
          col === 'fixed' ? '3rem' : `${col}fr`
        ).join(' '),
        '--fr-table-group__size': cols.length,
      }
    },
  },
}
</script>

<template>
  <div class="fr-table-group"
       :style="elementStyle">
    <slot />
  </div>
</template>

<style>
.fr-table-group {
  align-content: start;
  display: grid;
  grid-column-end: span var(--fr-table-group__size);
  overflow: hidden;
}
</style>
