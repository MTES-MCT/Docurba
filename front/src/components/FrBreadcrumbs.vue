<script setup lang="ts">
import type { Option } from '@/data/Option'
import BaseActionable from './BaseActionable.vue';

interface Props {
  value?: Array<Option<string>>
}

const {
  value = [],
} = defineProps<Props>()
</script>

<template>
  <ol class="fr-breadcrumbs">
    <li v-for="breadcrumb in value"
        :key="breadcrumb.value">
      <BaseActionable class="fr-breadcrumbs__link"
                      :to="breadcrumb.value">{{ breadcrumb.label }}</BaseActionable>
    </li>
    <li>
      <span class="fr-breadcrumbs__end">
        <slot />
      </span>
    </li>
  </ol>
</template>

<style>
.fr-breadcrumbs {
  align-items: center;
  column-gap: .25rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: start;
  list-style: none;
  margin-bottom: 0;
  margin-top: 0;
  padding-left: 0;
}
.fr-breadcrumbs li {
  align-items: center;
  column-gap: .25rem;
  display: grid;
  grid-auto-flow: column;
}
.fr-breadcrumbs li:not(:first-child)::before {
  background-color: var(--color-grey-425-625);
  content: '';
  height: 1rem;
  mask-image: url('@/assets/icons/arrow-right-s-line.svg');
  mask-size: 100% 100%;
  pointer-events: none;
  width: 1rem;
}
.fr-breadcrumbs__end,
.fr-breadcrumbs__link {
  display: grid;
  font-family: var(--font-family-sans);
  font-size: .75rem;
  font-weight: 400;
  line-height: 1.25rem;
}
.fr-breadcrumbs__end {
  color: var(--color-grey-200-850);
}
.fr-breadcrumbs__link {
  box-shadow: inset 0 -.0625rem 0 0 var(--color-grey-625-425);
  color: var(--color-grey-425-625);
  text-decoration: none;
}
.fr-breadcrumbs__link:focus,
.fr-breadcrumbs__link:hover {
  box-shadow: inset 0 -.0625rem 0 0 var(--color-grey-425-625);
}
</style>
