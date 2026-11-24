<script>
export default {
  props: {
    card: {
      default: false,
      type: Boolean
    },
    cols: {
      default: 'auto',
      type: String
    },
    top: {
      default: '0',
      type: String
    }
  },
  computed: {
    elementStyle () {
      return {
        '--du-table__cols': this.cols.split(' ').map(col =>
          col === 'fixed' ? '3rem' : `${col}fr`
        ).join(' '),
        '--du-table__top': this.top
      }
    }
  }
}
</script>

<template>
  <div
    class="du-table"
    :class="{ 'du-table--card': card }"
    :style="elementStyle"
  >
    <div class="du-table__header">
      <slot name="header" />
    </div>
    <div class="du-table__body">
      <slot />
    </div>
  </div>
</template>

<style>
.du-table {
  display: grid;
}
.du-table--card .du-table__body::after {
  box-shadow: inset .0625rem 0 0 0 #929292,
              inset -.0625rem 0 0 0 #929292,
              inset 0 -.0625rem 0 0 #929292;

}
.du-table--card .du-table-cell {
  padding-left: 1rem;
  padding-right: 1rem;
}
.du-table--card .du-table__header {
  box-shadow: inset .0625rem .0625rem 0 0 #929292,
              inset -.0625rem 0 0 0 #929292,
              inset 0 0 0 .0625rem #dddddd;
}
.du-table--card .du-table__header > .du-table-cell {
  box-shadow: inset 0 .0625rem 0 0 #929292,
              inset .0625rem 0 0 0 #dddddd;
  padding-bottom: 1rem;
  padding-top: 1rem;
}
.du-table--card .du-table__header > .du-table-cell:first-child {
  box-shadow: none;
}
.du-table--card .du-table-row {
  box-shadow: 0 -.0625rem 0 0 #929292;
}
.du-table--card .du-table-row--secondary {
  box-shadow: 0 -.0625rem 0 0 #dddddd;
}
.du-table__body {
  display: grid;
  position: relative;
}
.du-table__body::after {
  box-shadow: inset 0 -.0625rem 0 0 #dddddd;
  content: '';
  inset: 0;
  pointer-events: none;
  position: absolute;
}
.du-table__header {
  background-color: #f6f6f6;
  box-shadow: inset 0 -.0625rem 0 0 #dddddd;
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: var(--du-table__cols);
  position: sticky;
  top: var(--du-table__top);
  z-index: 1;
}
.du-table__header > .du-table-cell {
  align-items: center;
  color: #161616;
  font-weight: 700;
}
.du-table__header > .du-table-cell > .v-icon {
  color: #000091 !important;
}
</style>
