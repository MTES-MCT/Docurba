<script setup lang="ts">
import BaseActionable from '@/components/BaseActionable.vue'
import type { Option } from '@/data/Option'

interface Props {
  options: Array<Option<string>>
}

const {
  options,
} = defineProps<Props>()
</script>

<template>
  <nav class="fr-sidemenu">
    <BaseActionable v-for="option in options"
                    :key="option.value"
                    class="fr-sidemenu__link"
                    :to="option.value">{{ option.label }}</BaseActionable>
  </nav>
</template>

<style>
.fr-sidemenu {
  align-content: start;
  box-shadow: inset 0 -.0625rem 0 0 var(--color-grey-900-175);
  display: grid;
  padding-bottom: 1rem;
}
.fr-sidemenu__link {
  color: var(--color-grey-50-1000);
  cursor: pointer;
  font-family: var(--font-family-sans);
  font-size: 1rem;
  font-weight:700;
  line-height: 1.5rem;
  padding: .75rem 1rem;
  position: relative;
  text-decoration: none;
}
.fr-sidemenu__link:focus,
.fr-sidemenu__link:hover {
  background-color: var(--color-grey-1000-50-hover);
}
.fr-sidemenu__link.fr-link--exact-active {
  color: var(--color-blue-france-sun-113-625);
}
.fr-sidemenu__link.fr-link--exact-active::before {
  background-color: currentColor;
  bottom: .75rem;
  content: '';
  left: 0;
  position: absolute;
  top: .75rem;
  width: .125rem;
}

@media (min-width: 48rem) {
  .fr-sidemenu {
    box-shadow: inset -.0625rem 0 0 0 var(--color-grey-900-175);
    padding-bottom: 0;
    padding-right: 1rem;
  }
}

@media (min-width: 62rem) {
  .fr-sidemenu {
    padding-right: 1.5rem;
  }
}
</style>
