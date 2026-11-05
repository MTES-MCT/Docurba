<script>
export default {
  props: {
    secondary: {
      default: false,
      type: Boolean,
    },
    to: {
      default: undefined,
      type: [String, Object],
    },
  },
  computed: {
    actionable() {
      return !!this.to || !!this.$listeners.actuated
    },
  },
}
</script>

<template>
  <component :is="actionable ? 'FRActionable' : 'div'"
             class="fr-table-row"
             :class="{ 'fr-table-row--secondary': secondary }"
             :to="to"
             @actuated="$emit('actuated', $event)">
    <slot />
  </component>
</template>

<style>
.fr-table-row {
  box-shadow: 0 -.0625rem 0 0 var(--fr-color__grey-625-425);
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: var(--fr-table__cols);
}
a.fr-table-row,
.fr-table-row[tabindex] {
  cursor: pointer;
  text-decoration: none;
}
a.fr-table-row:focus-visible,
a.fr-table-row:hover,
.fr-table-row[tabindex]:focus-visible,
.fr-table-row[tabindex]:hover {
  background-color: var(--fr-color__grey-1000-50--hover);
}
.fr-table-row--secondary {
  box-shadow: 0 -.0625rem 0 0 var(--fr-color__grey-900-175);
}
</style>
