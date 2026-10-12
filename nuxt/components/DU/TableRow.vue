<script>
export default {
  props: {
    primary: {
      default: false,
      type: Boolean
    },
    to: {
      required: true,
      type: [String, Object]
    }
  }
}
</script>

<template>
  <NuxtLink
    class="du-table-row"
    :class="{ 'du-table-row--primary': primary }"
    :to="to"
  >
    <slot />
  </NuxtLink>
</template>

<style>
.du-table-row {
  box-shadow: inset 0 .0625rem 0 0 #ddd;
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: var(--du-table__cols);
  text-decoration: none;
}
.du-table-row:focus-visible,
.du-table-row:hover {
  background-color: #f6f6f6;
}
.du-table-row:last-child {
  box-shadow: inset 0 .0625rem 0 0 #ddd,
              inset 0 -.0625rem 0 0 #929292;
}
.du-table-row--primary:not(:first-child) {
  box-shadow: inset 0 .0625rem 0 0 #161616;
}
.du-table-row--primary:last-child {
  box-shadow: inset 0 .0625rem 0 0 #161616,
              inset 0 -.0625rem 0 0 #929292;
}
</style>
