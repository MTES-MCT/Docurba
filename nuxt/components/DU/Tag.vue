<script>
export default {
  props: {
    actionableChild: {
      default: false,
      type: Boolean
    },
    disabled: {
      default: false,
      type: Boolean
    },
    to: {
      default: undefined,
      type: [String, Object]
    },
    // Sizes
    sm: {
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
    :is="actionable ? 'FRActionable' : 'div'"
    class="du-tag"
    :class="{
      'du-tag--actionable-child': actionableChild,
      'du-tag--sm': sm,
    }"
    :disabled="actionable ? disabled : undefined"
    :to="to"
    @actuated="$emit('actuated', $event)"
  >
    <slot />
  </component>
</template>

<style>
.du-tag {
  --du-tag__bg: #eeeeee;
  --du-tag__bg-active: #eeeeee;
  --du-tag__color: #161616;

  align-items: center;
  background-color: var(--du-tag__bg);
  border-radius: 1rem;
  color: var(--du-tag__color);
  column-gap: .5rem;
  display: grid;
  font-size: .875rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.5rem;
  padding: .25rem .75rem;
}
.du-tag:focus-visible,
.du-tag:hover {
  background-color: var(--du-tag__bg-active);
}
.du-tag > .fr-icon {
  --fr-icon__size: 1rem;

  margin: .25rem -.25rem;
}
.du-tag[disabled] {
  --du-tag__bg: #e5e5e5;
  --du-tag__bg-active: #e5e5e5;
  --du-tag__color: #929292;

  cursor: not-allowed;
}
a.du-tag,
.du-tag[tabindex],
.du-tag--actionable-child {
  --du-tag__bg: #e3e3fd;
  --du-tag__color: #000091;
}
a.du-tag,
.du-tag[tabindex] {
  --du-tag__bg-active: #c1c1fb;

  cursor: pointer;
  text-decoration: none;
}
.du-tag--actionable-child {
  --du-tag__bg-active: #e3e3fd;
}
/* Sizes */
.du-tag--sm {
  border-radius: .75rem;
  column-gap: .375rem;
  font-size: .75rem;
  line-height: 1.25rem;
  padding: .125rem .5rem;
}
.du-tag--sm > .v-icon {
  margin-left: -.125rem;
  margin-right: -.125rem;
}
</style>
