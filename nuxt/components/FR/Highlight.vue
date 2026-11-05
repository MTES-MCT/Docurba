<script>
export default {
  props: {
    alt: {
      default: false,
      type: Boolean,
    },
  },
}
</script>

<template>
  <div class="fr-highlight"
       :class="{ 'fr-highlight--alt': alt }">
    <slot />
  </div>
</template>

<style>
.fr-highlight {
  background-color: var(--fr-color__blue-france-975-75);
  box-shadow: none;
  display: grid;
}
.fr-highlight--alt {
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: inset 0 -.0625rem 0 0 var(--fr-color__grey-900-175);
}
</style>
