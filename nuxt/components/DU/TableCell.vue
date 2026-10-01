<script>
export default {
  props: {
    link: {
      default: false,
      type: Boolean
    },
    primary: {
      default: false,
      type: Boolean
    }
  }
}
</script>

<template>
  <div
    class="du-table-cell"
    :class="{
      'du-table-cell--link': link,
      'du-table-cell--primary': primary
    }"
  >
    <slot />
  </div>
</template>

<style>
.du-table-cell {
  align-content: center;
  align-items: start;
  color: #3a3a3a;
  column-gap: .5rem;
  display: grid;
  font-size: .875rem;
  font-weight: 400;
  grid-auto-flow: column;
  justify-content: start;
  line-height: 1.25rem;
  padding: .5rem 1rem;
  min-width: 100%;
  width: 0;
}
.du-table-cell:first-child {
  box-shadow: inset .0625rem 0 0 0 #929292;
}
.du-table-cell:last-child {
  box-shadow: inset -.0625rem 0 0 0 #929292;
}
.du-table-cell .du-tag {
  margin-bottom: -.125rem;
  margin-top: -.125rem;
}
.du-table-cell .v-icon {
  color: inherit;
  margin-bottom: .125rem;
  margin-top: .125rem;
}
.du-table-cell--link {
  color: #000091;
}
.du-table-cell--primary {
  font-weight: 800;
}
</style>
