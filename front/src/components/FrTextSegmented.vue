<template>
  <p class="fr-text fr-text-segmented">
    <slot />
  </p>
</template>

<style>
.fr-text-segmented {
  column-gap: .5rem;
  display: flex;
  flex-wrap: wrap;
}
.fr-text-segmented > * {
  column-gap: .5rem;
  display: grid;
  grid-auto-flow: column;
}
.fr-text-segmented > *:not(:first-child)::before {
  content: '•';
}
</style>
