<script setup lang="ts">
import BaseActionable from '@/components/BaseActionable.vue'
</script>

<template>
  <BaseActionable class="fr-table-link">
    <slot />
  </BaseActionable>
</template>

<style>
.fr-table-link {
  align-items: center;
  color: var(--color-blue-france-sun-113-625);
  display: grid;
  font-family: var(--font-family-sans);
  font-size: 1rem;
  font-weight: 400;
  grid-auto-flow: column;
  height: 1.5rem;
  justify-content: start;
  line-height: 1.5rem;
  margin-left: -.5rem;
  margin-right: -.5rem;
  overflow: hidden;
  text-decoration: none;
  white-space: nowrap;
  width: 1.5rem;
}
.fr-table-link::before {
  background-color: currentColor;
  content: '';
  height: 1rem;
  margin: .25rem;
  mask-image: url('@/assets/icons/arrow-right-line.svg');
  mask-size: 100% 100%;
  pointer-events: none;
  width: 1rem;
}
</style>
