<script setup lang="ts">
import BaseActionable from '@/components/BaseActionable.vue'
</script>

<template>
  <BaseActionable class="fr-link">
    <slot />
  </BaseActionable>
</template>

<style>
.fr-link {
  box-shadow: inset 0 -.0625rem 0 0 currentColor;
  color: var(--color-blue-france-sun-113-625);
  cursor: pointer;
  text-decoration: none;
}
.fr-link:focus,
.fr-link:hover {
  box-shadow: inset 0 -.0625rem 0 0 currentColor,
              0 .0625rem 0 0 currentColor;
}
</style>
