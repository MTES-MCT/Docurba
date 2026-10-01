<script>
export default {
  props: {
    disabled: {
      default: false,
      type: Boolean
    },
    primary: {
      default: false,
      type: Boolean
    },
    to: {
      default: null,
      type: [String, Object]
    }
  }
}
</script>

<template>
  <DUActionable
    class="du-button"
    :class="{ 'du-button--primary': primary }"
    :disabled="disabled"
    :to="to"
    @actuated="$emit('actuated', $event)"
  >
    <slot />
  </DUActionable>
</template>

<style>
.du-button {
  align-items: center;
  background-color: #fff;
  box-shadow: inset 0 0 0 .0625rem #ddd;
  color: #000091 !important;
  column-gap: .5rem;
  display: grid;
  font-size: 1rem;
  font-weight: 500;
  grid-auto-flow: column;
  line-height: 1.5rem;
  padding: .5rem .75rem;
  text-decoration: none;
}
.du-button .v-icon {
  color: inherit;
}
.du-button--primary {
  background-color: #000091;
  box-shadow: none;
  color: #f5f5f5 !important;
}
</style>
