<template>
  <fieldset class="fr-fieldset">
    <slot />
  </fieldset>
</template>

<style>
.fr-fieldset {
  border: none;
  display: grid;
  margin-left: 0;
  margin-right: 0;
  padding: 0;
  row-gap: 1rem;
}
.fr-fieldset .fr-text {
  margin-top: -.25rem;
}
</style>
