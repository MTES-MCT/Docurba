<script>
export default {
  props: {
    link: {
      default: false,
      type: Boolean
    },
    to: {
      default: undefined,
      type: [String, Object]
    },
    vertical: {
      default: false,
      type: Boolean
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
    class="du-table-cell"
    :class="{
      'du-table-cell--link': link,
      'du-table-cell--vertical': vertical
    }"
    :to="to"
  >
    <slot />
  </component>
</template>

<style>
.du-table-cell {
  align-items: start;
  color: #3a3a3a;
  display: grid;
  font-size: .875rem;
  gap: .5rem;
  grid-auto-flow: column;
  justify-content: start;
  line-height: 1.5rem;
  overflow: hidden;
  padding: .5rem;
}
a.du-table-cell,
.du-table-cell[tabindex],
.du-table-cell--link {
  color: #000091;
}
a.du-table-cell,
.du-table-cell[tabindex] {
  cursor: pointer;
  text-decoration: none;
}
a.du-table-cell:focus-visible,
a.du-table-cell:hover,
.du-table-cell[tabindex]:focus-visible,
.du-table-cell[tabindex]:hover {
  background-color: #f6f6f6;
}
.du-table-cell > .du-badge--sm {
  margin-bottom: .125rem;
  margin-top: .125rem;
}
.du-table-cell > .du-field--checkbox {
  margin-bottom: -.5rem;
  margin-top: -.5rem;
}
.du-table-cell > .v-icon {
  color: inherit !important;
  margin-bottom: .25rem;
  margin-top: .25rem;
}
.du-table-cell--vertical {
  grid-auto-flow: row;
  justify-items: start;
}
</style>
