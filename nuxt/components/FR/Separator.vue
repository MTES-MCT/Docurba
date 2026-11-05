<template>
  <div class="fr-separator">
    <FRText v-if="$slots.default"
            sm>
      <strong>
        <slot />
      </strong>
    </FRText>
  </div>
</template>

<style>
.fr-separator {
  align-items: center;
  column-gap: .75rem;
  display: grid;
  grid-auto-columns: 1fr auto 1fr;
  grid-auto-flow: column;
  text-align: center;
  text-transform: uppercase;
}
.fr-separator:empty {
  column-gap: 0;
}
.fr-separator::before,
.fr-separator::after {
  background-color: var(--fr-color__grey-900-175);
  content: '';
  height: .0625rem;
}
</style>
