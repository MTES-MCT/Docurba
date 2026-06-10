<script setup lang="ts">
interface Props {
  end?: boolean
}

const {
  end = false,
} = defineProps<Props>()
</script>

<template>
  <div class="fr-buttons"
       :class="{ 'fr-buttons--end': end }">
    <slot />
  </div>
</template>

<style>
.fr-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.fr-buttons--end {
  justify-content: end;
}
</style>
