<script>
import { mdiCircle } from '@mdi/js'

export default {
  props: {
    value: {
      default: () => [],
      type: Array,
    },
  },
  data() {
    return {
      icons: {
        mdiCircle,
      },
    }
  },
}
</script>

<template>
  <div v-if="value.length"
       class="fr-menu">
    <FRContainer>
      <FRActionable v-for="item, index in value"
                    :key="index"
                    class="fr-menu__item"
                    :class="{ 'fr-menu__item--active': item.active }"
                    :to="item.to">
        {{ item.label }}
        <FRIcon v-if="item.highlighted"
                :value="icons.mdiCircle" />
      </FRActionable>
    </FRContainer>
  </div>
</template>

<style>
.fr-menu {
  box-shadow: inset 0 .0625rem 0 0 var(--fr-color__grey-900-175);
  display: grid;
}
.fr-menu > .fr-container {
  column-gap: 1rem;
  grid-auto-flow: column;
  justify-content: start;
}
.fr-menu__item {
  align-items: center;
  color: var(--fr-color__grey-50-1000);
  column-gap: .5rem;
  display: grid;
  font-size: .875rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.5rem;
  padding: 1rem;
  text-decoration: none;
}
.fr-menu__item:focus-visible,
.fr-menu__item:hover {
  background-color: var(--fr-color__grey-1000-50--hover);
}
.fr-menu__item > .fr-icon {
  --fr-icon__size: 1rem;

  color: var(--fr-color__yellow-moutarde-850-200);
}
.fr-menu__item--active {
  box-shadow: inset 0 -.125rem 0 0 var(--fr-color__blue-france-sun-113-625);
  color: var(--fr-color__blue-france-sun-113-625);
}
</style>
