<script>
import { mdiArrowRight } from '@mdi/js'

export default {
  props: {
    alt: {
      default: false,
      type: Boolean,
    },
    borderless: {
      default: false,
      type: Boolean,
    },
    lg: {
      default: false,
      type: Boolean,
    },
    raised: {
      default: false,
      type: Boolean,
    },
    to: {
      default: undefined,
      type: [String, Object],
    },
  },
  data() {
    return {
      icons: {
        mdiArrowRight,
      },
    }
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
             class="fr-card"
             :class="{
               'fr-card--alt': alt,
               'fr-card--borderless': borderless,
               'fr-card--lg': lg,
               'fr-card--raised': raised,
             }"
             :to="to"
             @actuated="$emit('actuated', $event)">
    <slot />
    <FRIcon v-if="actionable"
            :value="icons.mdiArrowRight" />
  </component>
</template>

<style>
.fr-card {
  align-content: space-between;
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: 0 0 0 .0625rem var(--fr-color__grey-900-175);
  display: grid;
  padding: 1rem;
  row-gap: .5rem;
}
a.fr-card,
.fr-card[tabindex] {
  cursor: pointer;
  text-decoration: none;
}
a.fr-card:focus-visible,
a.fr-card:hover,
.fr-card[tabindex]:focus-visible,
.fr-card[tabindex]:hover {
  background-color: var(--fr-color__grey-1000-50--hover);
}
.fr-card > .fr-icon {
  --fr-icon__size: 1rem;

  color: var(--fr-color__blue-france-sun-113-625);
  justify-self: end;
}
.fr-card--alt {
  background-color: var(--fr-color__grey-975-75);
}
.fr-card--borderless {
  box-shadow: none;
}
.fr-card--lg {
  padding: 2rem;
}
.fr-card--raised {
  box-shadow: 0 0 0 .0625rem var(--fr-color__grey-900-175),
              var(--fr-shadow__raised);
}

@media (min-width: 62rem) {
  .fr-card {
    padding: 1.5rem;
  }
  .fr-card--lg {
    padding: 3rem;
  }
}
</style>
