<script>
export default {
  props: {
    disabled: {
      default: false,
      type: Boolean
    },
    to: {
      default: undefined,
      type: [String, Object]
    }
  }
}
</script>

<template>
  <DUActionable
    class="du-link"
    :disabled="disabled"
    :to="to"
    @actuated="$emit('actuated', $event)"
  >
    <slot />
  </DUActionable>
</template>

<style>
.du-link {
  align-items: center;
  box-shadow: inset 0 -.0625rem 0 0 currentColor;
  color: #000091;
  column-gap: .5rem;
  cursor: pointer;
  display: grid;
  font-size: 1rem;
  font-weight: 500;
  grid-auto-flow: column;
  line-height: 1.5rem;
  text-decoration: none;
}
.du-link:focus-visible,
.du-link:hover {
  box-shadow: inset 0 -.125rem 0 0 currentColor;
}
.du-link .v-icon {
  color: inherit;
}
</style>
