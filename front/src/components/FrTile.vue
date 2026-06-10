<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'
import BaseActionable from '@/components/BaseActionable.vue'

interface Props {
  to?: string | RouteLocationRaw | null
}

const {
  to = null,
} = defineProps<Props>()
</script>

<template>
  <div class="fr-link-container fr-tile"
       :class="{ 'fr-tile--disabled': !to }">
    <p class="fr-tile__title">
      <BaseActionable class="fr-tile__link"
                      :disabled="!to"
                      :to="to">
        <slot name="title" />
      </BaseActionable>
    </p>
    <p v-if="$slots.description"
       class="fr-tile__description">
      <slot name="description" />
    </p>
  </div>
</template>

<style>
.fr-tile {
  align-content: start;
  background-color: var(--color-grey-1000-50);
  box-shadow: inset 0 -.25rem 0 0 var(--color-blue-france-sun-113-625),
              inset 0 0 0 .0625rem var(--color-grey-900-175);
  display: grid;
  justify-content: center;
  padding: 2rem 2rem 2.25rem;
  row-gap: .5rem;
}
.fr-tile:not(.fr-tile--disabled):focus-within,
.fr-tile:not(.fr-tile--disabled):hover {
  background-color: var(--color-grey-1000-50-hover);
}
.fr-tile--disabled {
  box-shadow: inset 0 -.25rem 0 0 var(--color-grey-925-125),
              inset 0 0 0 .0625rem var(--color-grey-900-175);
  cursor: not-allowed;
}
.fr-tile--disabled .fr-tile__link {
  color: var(--color-grey-625-425);
}
.fr-tile__description {
  color: var(--color-grey-200-850);
  font-family: var(--font-family-sans);
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5rem;
  margin-bottom: 0;
  margin-top: 0;
  text-align: center;
}
.fr-tile__link {
  color: var(--color-blue-france-sun-113-625);
}
.fr-tile__title {
  display: grid;
  font-family: var(--font-family-sans);
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.5rem;
  margin-bottom: 0;
  margin-top: 0;
  text-align: center;
}

@media (min-width: 48rem) {
  .fr-tile__title {
    font-size: 1.25rem;
    line-height: 1.75rem;
  }
}
</style>
