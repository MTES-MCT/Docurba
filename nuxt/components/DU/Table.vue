<template>
  <div class="du-table">
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
.du-table__body {
  display: grid;
}
.du-table__header {
  background-color: #f6f6f6;
  box-shadow: inset 0 .0625rem 0 0 #929292;
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: var(--du-table__cols);
}
.du-table__header .du-table-cell {
  box-shadow: inset .0625rem 0 0 0 #ddd;
  font-weight: 700;
  padding-bottom: 1.125rem;
  padding-top: 1.125rem;
}
.du-table__header .du-table-cell:first-child {
  box-shadow: inset .0625rem 0 0 0 #929292;
}
.du-table__header .du-table-cell:last-child {
  box-shadow: inset .0625rem 0 0 0 #ddd,
              inset -.0625rem 0 0 0 #929292;
}
</style>
