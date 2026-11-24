<script>
export default {
  props: {
    secondary: {
      default: false,
      type: Boolean
    },
    to: {
      default: undefined,
      type: [String, Object]
    }
  },
  computed: {
    actionable () {
      return !!this.to || !!this.$listeners.actuated
    }
  }
}
</script>

<template>
  <component
    :is="actionable ? 'DUActionable' : 'div'"
    class="du-table-row"
    :class="{ 'du-table-row--secondary': secondary }"
    :to="to"
    @actuated="$emit('actuated', $event)"
  >
    <slot />
  </component>
</template>

<style>
.du-table-row {
  box-shadow: 0 -.0625rem 0 0 #dddddd;
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: var(--du-table__cols);
}
a.du-table-row,
.du-table-row[tabindex] {
  cursor: pointer;
  text-decoration: none;
}
a.du-table-row:focus-visible,
a.du-table-row:hover,
.du-table-row[tabindex]:focus-visible,
.du-table-row[tabindex]:hover {
  background-color: #f6f6f6;
}
.du-table-row--secondary {
  box-shadow: none;
}
</style>
