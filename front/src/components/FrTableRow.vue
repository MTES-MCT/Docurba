<script setup lang="ts">
interface Props {
  joined?: boolean
}

const {
  joined = false,
} = defineProps<Props>()
</script>

<template>
  <tr class="fr-table-row"
      :class="{ 'fr-table-row--joined': joined }">
    <slot />
  </tr>
</template>

<style>
.fr-table-row td {
  box-shadow: inset 0 -.0625rem 0 0 var(--color-grey-625-425);
}
.fr-table-row--joined td {
  box-shadow: inset 0 -.0625rem 0 0 var(--color-grey-900-175);
}
</style>
