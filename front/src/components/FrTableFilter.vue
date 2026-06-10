<script setup lang="ts">
import FrButton from '@/components/FrButton.vue'
</script>

<template>
  <div class="fr-table-filter">
    <slot />
    <FrButton class="fr-icon--before fr-icon--before-filter-line"
              icon
              sm
              tertiary>
      <slot name="action" />
    </FrButton>
  </div>
</template>

<style>
.fr-table-filter {
  align-items: center;
  column-gap: 1rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: space-between;
}
</style>
