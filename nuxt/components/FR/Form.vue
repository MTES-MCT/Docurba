<template>
  <form class="fr-form">
    <slot />
  </form>
</template>

<style>
.fr-form {
  display: grid;
  row-gap: 1rem;
}

@media (min-width: 62rem) {
  .fr-form {
    row-gap: 1.5rem;
  }
}
</style>
