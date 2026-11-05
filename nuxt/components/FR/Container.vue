<script>
export default {
  props: {
    sm: {
      default: false,
      type: Boolean,
    },
  },
}
</script>

<template>
  <div class="fr-container"
       :class="{ 'fr-container--sm': sm }">
    <slot />
  </div>
</template>

<style>
.fr-container {
  display: grid;
  margin-left: auto;
  margin-right: auto;
  max-width: 78rem;
  padding-left: 1rem;
  padding-right: 1rem;
  width: 100%;
}
.fr-container--sm {
  max-width: 53rem;
}

@media (min-width: 62rem) {
  .fr-container {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
}
</style>
