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
    // Alignements
    between: {
      default: false,
      type: Boolean,
    },
    start: {
      default: false,
      type: Boolean,
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
    // Variations
    secondary: {
      default: false,
      type: Boolean,
    },
    tertiary: {
      default: false,
      type: Boolean,
    },
    tertiaryBorderless: {
      default: false,
      type: Boolean,
    },
  },
}
</script>

<template>
  <FRActionable class="fr-button"
                :class="{
                  'fr-button--between': between,
                  'fr-button--lg': lg,
                  'fr-button--secondary': secondary,
                  'fr-button--sm': sm,
                  'fr-button--start': start,
                  'fr-button--tertiary': tertiary,
                  'fr-button--tertiary-borderless': tertiaryBorderless,
                }"
                :disabled="disabled"
                :to="to"
                @actuated="$emit('actuated', $event)">
    <slot />
  </FRActionable>
</template>

<style>
.fr-button {
  --fr-button__bg: var(--fr-color__blue-france-sun-113-625);
  --fr-button__bg-active: var(--fr-color__blue-france-sun-113-625--hover);
  --fr-button__border: transparent;
  --fr-button__color: var(--fr-color__blue-france-975-sun-113);

  align-items: center;
  background-color: var(--fr-button__bg);
  box-shadow: inset 0 0 0 .0625rem var(--fr-button__border);
  color: var(--fr-button__color);
  column-gap: .75rem;
  cursor: pointer;
  display: grid;
  font-size: 1rem;
  font-weight: 500;
  grid-auto-flow: column;
  justify-content: center;
  line-height: 1.5rem;
  padding: .5rem 1rem;
  text-decoration: none;
}
.fr-button:focus-visible,
.fr-button:hover {
  background-color: var(--fr-button__bg-active);
}
.fr-button > .fr-icon {
  --fr-icon__size: 1rem;

  margin: .25rem -.25rem;
}
.fr-button[disabled] {
  --fr-button__bg: var(--fr-color__grey-925-125);
  --fr-button__bg-active: var(--fr-button__bg);
  --fr-button__border: transparent;
  --fr-button__color: var(--fr-color__grey-625-425);

  cursor: not-allowed;
}
/* Alignments */
.fr-button--between {
  justify-content: space-between;
}
.fr-button--start {
  justify-content: start;
}
/* Sizes */
.fr-button--lg {
  column-gap: 1.25rem;
  font-size: 1.125rem;
  line-height: 1.75rem;
  padding: .625rem 1.5rem;
}
.fr-button--lg > .fr-icon {
  --fr-icon__size: 1.5rem;

  margin: .125rem -.75rem;
}
.fr-button--sm {
  font-size: .875rem;
  padding: .25rem .75rem;
}
/* Variations */
.fr-button--secondary,
.fr-button--tertiary,
.fr-button--tertiary-borderless {
  --fr-button__bg: var(--fr-color__grey-1000-50);
  --fr-button__bg-active: var(--fr-color__grey-1000-50--hover);
  --fr-button__color: var(--fr-color__blue-france-sun-113-625);
}
.fr-button--secondary {
  --fr-button__border: var(--fr-color__blue-france-sun-113-625);
}
.fr-button--tertiary {
  --fr-button__border: var(--fr-color__grey-900-175);
}
.fr-button--tertiary-borderless {
  --fr-button__border: transparent;
}
.fr-button--secondary[disabled],
.fr-button--tertiary[disabled],
.fr-button--tertiary-borderless[disabled] {
  --fr-button__bg: transparent;
  --fr-button__color: var(--fr-color__grey-625-425);
}
.fr-button--secondary[disabled],
.fr-button--tertiary[disabled] {
  --fr-button__border: var(--fr-color__grey-925-125);
}
.fr-button--tertiary-borderless[disabled] {
  --fr-button__border: transparent;
}
</style>
