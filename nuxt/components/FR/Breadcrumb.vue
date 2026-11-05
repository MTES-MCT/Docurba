<script>
import { mdiChevronRight } from '@mdi/js'

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
        mdiChevronRight,
      },
    }
  },
}
</script>

<template>
  <ol class="fr-breadcrumb">
    <FRText v-for="item, index in value"
            :key="index"
            tag="li"
            xs>
      <FRActionable class="fr-breadcrumb__link"
                    :to="item.to">
        {{ item.label }}
      </FRActionable>
      <FRIcon :value="icons.mdiChevronRight" />
    </FRText>
    <FRText tag="li"
            xs>
      <slot />
    </FRText>
  </ol>
</template>

<style>
.fr-breadcrumb {
  align-items: center;
  column-gap: .5rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: start;
  list-style: none;
}
.fr-breadcrumb > li {
  align-items: center;
  column-gap: .5rem;
  display: grid;
  grid-auto-flow: column;
}
.fr-breadcrumb > li > .fr-icon {
  --fr-icon__size: 1rem;

  color: var(--fr-color__grey-425-625);
}
.fr-breadcrumb__link {
  box-shadow: inset 0 -.0625rem 0 0 var(--fr-color__grey-425-625);
  color: var(--fr-color__grey-425-625);
  cursor: pointer;
  text-decoration: none;
}
.fr-breadcrumb__link:focus-visible,
.fr-breadcrumb__link:hover {
  box-shadow: inset 0 -.125rem 0 0 var(--fr-color__grey-425-625);
}
</style>
