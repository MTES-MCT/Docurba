<script>
import { mdiChevronDown } from '@mdi/js'

export default {
  props: {
    card: {
      default: false,
      type: Boolean,
    },
    label: {
      default: '',
      type: String,
    },
    value: {
      default: false,
      type: Boolean,
    },
  },
  data() {
    return {
      icons: {
        mdiChevronDown,
      },
    }
  },
}
</script>

<template>
  <div class="fr-accordion"
       :class="{ 'fr-accordion--card': card }">
    <FRActionable class="fr-accordion__action"
                  @actuated="$emit('input', !value)">
      {{ label }}
      <FRIcon :value="icons.mdiChevronDown" />
    </FRActionable>
    <div v-if="value"
         class="fr-accordion__body">
      <slot />
    </div>
  </div>
</template>

<style>
.fr-accordion {
  background-color: var(--fr-color__grey-1000-50);
  display: grid;
  position: relative;
}
.fr-accordion::after {
  box-shadow: inset 0 .0625rem 0 0 var(--fr-color__grey-900-175),
              inset 0 -.0625rem 0 0 var(--fr-color__grey-900-175);
  content: '';
  inset: 0;
  pointer-events: none;
  position: absolute;
}
.fr-accordion--card::after {
  box-shadow: inset 0 0 0 .0625rem var(--fr-color__grey-900-175);
}
.fr-accordion--card > .fr-accordion__action {
  padding-bottom: 1rem;
  padding-top: 1rem;
}
.fr-accordion--card > .fr-accordion__action > .fr-icon {
  --fr-icon__size: 1.5rem;
}
.fr-accordion__action {
  align-items: center;
  color: var(--fr-color__blue-france-sun-113-625);
  cursor: pointer;
  display: grid;
  font-size: 1rem;
  font-weight: 500;
  grid-auto-flow: column;
  justify-content: space-between;
  line-height: 1.5rem;
  padding: .75rem 1rem;
}
.fr-accordion__action:focus-visible,
.fr-accordion__action:hover {
  background-color: var(--fr-color__grey-1000-50--hover);
}
.fr-accordion__action > .fr-icon {
  --fr-icon__size: 1rem;
}
.fr-accordion__action:not(:only-child) {
  background-color: var(--fr-color__blue-france-925-125);
}
.fr-accordion__action:not(:only-child):focus-visible,
.fr-accordion__action:not(:only-child):hover {
  background-color: var(--fr-color__blue-france-925-125--hover);
}
.fr-accordion__action:not(:only-child) > .fr-icon {
  transform: rotate(180deg);
}
.fr-accordion__body {
  display: grid;
  padding: 1rem;
}

@media (min-width: 62rem) {
  .fr-accordion--card > .fr-accordion__action,
  .fr-accordion--card > .fr-accordion__body {
    padding: 1.5rem;
  }
}
</style>
