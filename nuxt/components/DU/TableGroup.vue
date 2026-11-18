<script>
export default {
  props: {
    cols: {
      default: '',
      type: String
    }
  },
  computed: {
    elementStyle () {
      const cols = this.cols.split(' ')

      return {
        '--du-table__cols': cols.map(col =>
          col === 'fixed' ? '3rem' : `${col}fr`
        ).join(' '),
        '--du-table-group__size': cols.length
      }
    }
  }
}
</script>

<template>
  <div
    class="du-table-group"
    :style="elementStyle"
  >
    <slot />
  </div>
</template>

<style>
.du-table-group {
  align-content: start;
  display: grid;
  grid-column-end: span var(--du-table-group__size);
  overflow: hidden;
}
</style>
