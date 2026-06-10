<script setup lang="ts">
import BaseActionable from '@/components/BaseActionable.vue'
</script>

<template>
  <BaseActionable class="fr-tag">
    <slot />
  </BaseActionable>
</template>

<style>
.fr-tag {
  background-color: var(--color-blue-france-925-125);
  border-radius: .75rem;
  color: var(--color-blue-france-sun-113-625);
  font-family: var(--font-family-sans);
  font-size: .75rem;
  font-weight: 400;
  line-height: 1.25rem;
  padding: .125rem .5rem;
  width: fit-content;
}
.fr-tag:focus,
.fr-tag:hover {
  background-color: var(--color-blue-france-925-125-hover);
}
</style>
