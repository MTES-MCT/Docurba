<script>
export default {
  props: {
    alt: {
      default: false,
      type: Boolean,
    },
    sm: {
      default: false,
      type: Boolean,
    },
  },
}
</script>

<template>
  <div class="fr-container"
       :class="{
         'fr-container--alt': alt,
         'fr-container--sm': sm,
       }">
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
.fr-container--alt {
  background-color: var(--fr-color__grey-975-75);
}
.fr-container--sm {
  max-width: 37rem;
}

@media (min-width: 62rem) {
  .fr-container {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
  .fr-container--sm {
    padding-left: 6rem;
    padding-right: 6rem;
  }
}
</style>
