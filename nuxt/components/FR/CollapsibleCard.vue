<script>
import { mdiMenuDown } from '@mdi/js'

export default {
  props: {
    label: {
      default: '',
      type: String
    },
    value: {
      default: false,
      type: Boolean,
    },
  },
  data() {
    return {
      icons: {
        mdiMenuDown,
      },
    }
  },
}
</script>

<template>
  <div class="fr-collapsible-card"
       :class="{ 'fr-collapsible-card--active': value }">
    <FRCard raised>
      <slot name="header" />
    </FRCard>
    <div v-if="label"
         class="fr-collapsible-card__body">
      <FRActionable class="fr-collapsible-card__action"
                    @actuated="$emit('input', !value)">
        <FRIcon :value="icons.mdiMenuDown" />
        {{ value ? '' : label }}
      </FRActionable>
      <div v-if="value"
           class="fr-collapsible-card__content">
        <slot />
      </div>
    </div>
  </div>
</template>

<style>
.fr-collapsible-card {
  background-color: var(--fr-color__grey-975-75);
  display: grid;
  padding: 1rem;
  row-gap: 1rem;
}
.fr-collapsible-card__action {
  color: var(--fr-color__grey-425-625);
  column-gap: .5rem;
  cursor: pointer;
  display: grid;
  font-size: .875rem;
  font-weight: 400;
  grid-auto-flow: column;
  justify-content: start;
  line-height: 1.5rem;
  padding-left: .5rem;
  padding-right: .5rem;
}
.fr-collapsible-card__action > .fr-icon {
  --fr-icon__size: 2rem;

  color: var(--fr-color__blue-france-sun-113-625);
  margin-bottom: -.25rem;
  margin-top: -.25rem;
  pointer-events: none;
}
.fr-collapsible-card__action:not(:only-child) > .fr-icon {
  transform: rotate(180deg);
}
.fr-collapsible-card__body {
  column-gap: 1rem;
  display: grid;
  grid-auto-columns: 3rem 1fr;
  grid-auto-flow: column;
}
.fr-collapsible-card__content {
  display: grid;
  gap: 1rem;
}

@media (min-width: 36rem) {
  .fr-collapsible-card__body {
    grid-auto-columns: 1fr 16rem;
  }
}

@media (min-width: 48rem) {
  .fr-collapsible-card__body {
    grid-auto-columns: 1fr 33rem;
  }
  .fr-collapsible-card__content {
    grid-template-columns: 1fr 1fr;
  }
}

@media (min-width: 62rem) {
  .fr-collapsible-card {
    padding: 1.5rem;
  }
  .fr-collapsible-card__body {
    grid-auto-columns: 1fr 50rem;
  }
  .fr-collapsible-card__content {
    grid-template-columns: 1fr 1fr 1fr;
  }
}
</style>
