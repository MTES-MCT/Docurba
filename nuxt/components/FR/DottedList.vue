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
  <ul class="fr-dotted-list"
      :class="{ 'fr-dotted-list--sm': sm }">
    <slot />
  </ul>
</template>

<style>
.fr-dotted-list {
  column-gap: .5rem;
  display: flex;
  list-style: none;
}
.fr-dotted-list > li {
  align-items: center;
  color: var(--fr-color__grey-200-850);
  column-gap: .5rem;
  display: grid;
  font-size: 1rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.5rem;
}
.fr-dotted-list > li:not(:first-child)::before {
  content: '•';
}
.fr-dotted-list--sm > li {
  color: var(--fr-color__grey-425-625);
  font-size: .75rem;
  line-height: 1.25rem;
}
</style>
