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
  <div class="fr-badge"
       :class="{ 'fr-badge--sm': sm }">
    <slot />
  </div>
</template>

<style>
.fr-badge {
  --fr-badge__bg: var(--fr-color__grey-950-100);
  --fr-badge__border: transparent;
  --fr-badge__color: var(--fr-color__grey-200-850);

  background-color: var(--fr-badge__bg);
  border-radius: .25rem;
  box-shadow: inset 0 0 0 .0625rem var(--fr-badge__border);
  color: var(--fr-badge__color);
  column-gap: .5rem;
  display: grid;
  font-size: .875rem;
  font-weight: 700;
  grid-auto-flow: column;
  line-height: 1.5rem;
  padding-left: .5rem;
  padding-right: .5rem;
  text-transform: uppercase;
  white-space: nowrap;
}
.fr-badge > .fr-icon {
  --fr-icon__size: 1rem;

  margin: .25rem -.25rem;
}
.fr-badge--sm {
  column-gap: .375rem;
  font-size: .75rem;
  line-height: 1.25rem;
  padding-left: .375rem;
  padding-right: .375rem;
}
.fr-badge--sm > .fr-icon {
  --fr-icon__size: .75rem;

  margin-left: -.125rem;
  margin-right: -.125rem;
}
</style>
