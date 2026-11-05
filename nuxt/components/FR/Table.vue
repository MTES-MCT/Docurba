<script>
export default {
  props: {
    borderless: {
      default: false,
      type: Boolean,
    },
    card: {
      default: false,
      type: Boolean,
    },
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
       :class="{
         'fr-table--borderless': borderless,
         'fr-table--card': card,
       }"
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
.fr-table--borderless .fr-table__body::after {
  box-shadow: none;
}
.fr-table--borderless .fr-table-row {
  box-shadow: none;
}
.fr-table--card .fr-table__body::after {
  box-shadow: inset .0625rem 0 0 0 var(--fr-color__grey-625-425),
              inset -.0625rem 0 0 0 var(--fr-color__grey-625-425),
              inset 0 -.0625rem 0 0 var(--fr-color__grey-625-425);

}
.fr-table--card .fr-table-cell {
  padding-left: 1rem;
  padding-right: 1rem;
}
.fr-table--card .fr-table__header {
  background-color: var(--fr-color__grey-975-75);
  box-shadow: inset 0 0 0 .0625rem var(--fr-color__grey-625-425);
}
.fr-table--card .fr-table-row {
  box-shadow: 0 -.0625rem 0 0 var(--fr-color__grey-625-425);
}
.fr-table--card .fr-table-row--secondary {
  box-shadow: 0 -.0625rem 0 0 var(--fr-color__grey-900-175);
}
.fr-table__body {
  display: grid;
  position: relative;
}
.fr-table__body::after {
  box-shadow: inset 0 -.0625rem 0 0 var(--fr-color__grey-900-175);
  content: '';
  inset: 0;
  pointer-events: none;
  position: absolute;
}
.fr-table__header {
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: inset 0 -.0625rem 0 0 var(--fr-color__grey-900-175);
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: var(--fr-table__cols);
  position: sticky;
  top: var(--fr-header__size);
  z-index: var(--fr-index__table);
}
.fr-table__header > .fr-table-cell {
  align-items: center;
  color: var(--fr-color__grey-50-1000);
  font-weight: 700;
}
.fr-table__header > .fr-table-cell > .fr-icon {
  color: var(--fr-color__blue-france-sun-113-625);
}
</style>
