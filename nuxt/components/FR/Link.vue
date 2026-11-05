<script>
export default {
  props: {
    disabled: {
      default: false,
      type: Boolean,
    },
    to: {
      default: undefined,
      type: [String, Object],
    },
    // Sizes
    lg: {
      default: false,
      type: Boolean,
    },
    sm: {
      default: false,
      type: Boolean,
    },
  },
}
</script>

<template>
  <FRActionable class="fr-link"
                :class="{
                  'fr-link--lg': lg,
                  'fr-link--sm': sm,
                }"
                :disabled="disabled"
                :to="to"
                @actuated="$emit('actuated', $event)">
    <slot />
  </FRActionable>
</template>

<style>
.fr-link {
  align-items: center;
  box-shadow: inset 0 -.0625rem 0 0 currentColor;
  color: var(--fr-color__blue-france-sun-113-625);
  column-gap: .5rem;
  cursor: pointer;
  display: grid;
  font-size: 1rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.5rem;
  text-decoration: none;
}
.fr-link:focus-visible,
.fr-link:hover {
  box-shadow: inset 0 -.125rem 0 0 currentColor;
}
.fr-link > .fr-icon {
  --fr-icon__size: 1rem;
}
/* Sizes */
.fr-link--lg {
  font-size: 1.125rem;
  line-height: 1.75rem;
}
.fr-link--lg > .fr-icon {
  --fr-icon__size: 1.5rem;
}
.fr-link--sm {
  font-size: .875rem;
}
</style>
