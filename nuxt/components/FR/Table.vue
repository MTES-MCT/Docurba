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
      return {
        '--fr-table__cols': this.cols.split(' ').map((col) =>
          col === 'fixed' ? '3rem' : `${col}fr`
        ).join(' '),
      }
    },
  },
}
</script>

<template>
  <div class="fr-table"
       :style="elementStyle">
    <div class="fr-table__header">
      <slot name="header" />
    </div>
    <div class="fr-table__body">
      <slot />
    </div>
  </div>
</template>

<style>
.fr-table {
  display: grid;
}
.fr-table__body {
  background-color: var(--fr-color__grey-1000-50);
  display: grid;
  position: relative;
}
.fr-table__body::after {
  box-shadow: inset .0625rem 0 0 0 var(--fr-color__grey-625-425),
              inset -.0625rem 0 0 0 var(--fr-color__grey-625-425),
              inset 0 -.0625rem 0 0 var(--fr-color__grey-625-425);
  content: '';
  inset: 0;
  pointer-events: none;
  position: absolute;
}
.fr-table__header {
  background-color: var(--fr-color__grey-975-75);
  box-shadow: inset 0 0 0 .0625rem var(--fr-color__grey-625-425);
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: var(--fr-table__cols);
  position: sticky;
  top: var(--fr-header__size);
  z-index: var(--fr-index__table);
}
.fr-table__header > .fr-table-cell {
  font-weight: 700;
}
.fr-table__header > .fr-table-cell > .fr-icon {
  color: var(--fr-color__blue-france-sun-113-625);
}
</style>
