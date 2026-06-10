<template>
  <p class="fr-badge">
    <slot />
  </p>
</template>

<style>
.fr-badge {
  align-items: center;
  background-color: var(--color-grey-950-100);
  border-radius: .25rem;
  color: var(--color-grey-200-850);
  column-gap: .25rem;
  display: grid;
  font-family: var(--font-family-sans);
  font-size: .75rem;
  font-weight: 700;
  grid-auto-flow: column;
  line-height: 1.25rem;
  margin-bottom: 0;
  margin-top: 0;
  padding: .125rem .5rem;
  text-transform: uppercase;
  width: fit-content;
}
.fr-badge::before {
  margin-left: -.125rem;
}
</style>
