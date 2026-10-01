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
    sm: {
      default: false,
      type: Boolean
    },
    tertiary: {
      default: false,
      type: Boolean
    },
    tertiaryBorderless: {
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
    class="du-button"
    :class="{
      'du-button--primary': primary,
      'du-button--sm': sm,
      'du-button--tertiary': tertiary,
      'du-button--tertiary-borderless': tertiaryBorderless
    }"
    :disabled="disabled"
    :to="to"
    @actuated="$emit('actuated', $event)"
  >
    <slot />
  </DUActionable>
</template>

<style>
.du-button {
  column-gap: .75rem;
  cursor: pointer;
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
  margin: .25rem -.25rem;
}
.du-button[disabled] {
  cursor: default;
}
.du-button--primary {
  background-color: #000091;
  color: #f5f5f5 !important;
}
.du-button--primary:focus-visible,
.du-button--primary:hover {
  background-color: #1212ff;
}
.du-button--sm {
  font-size: .875rem;
  padding-bottom: .25rem;
  padding-top: .25rem;
}
.du-button--tertiary,
.du-button--tertiary-borderless {
  background-color: #fff;
  color: #000091 !important;
}
.du-button--tertiary {
  box-shadow: inset 0 0 0 .0625rem #ddd;
}
.du-button--tertiary:focus-visible,
.du-button--tertiary:hover,
.du-button--tertiary-borderless:focus-visible,
.du-button--tertiary-borderless:hover {
  background-color: #f6f6f6;
}
</style>
