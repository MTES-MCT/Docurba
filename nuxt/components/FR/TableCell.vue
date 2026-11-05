<script>
export default {
  props: {
    link: {
      default: false,
      type: Boolean,
    },
  },
}
</script>

<template>
  <div class="fr-table-cell"
       :class="{ 'fr-table-cell--link': link }">
    <slot />
  </div>
</template>

<style>
.fr-table-cell {
  align-items: start;
  color: var(--fr-color__grey-200-850);
  column-gap: .5rem;
  display: grid;
  font-size: .875rem;
  grid-auto-flow: column;
  justify-content: start;
  line-height: 1.5rem;
  padding: .5rem 1rem;
}
.fr-table-cell > .fr-badge--sm {
  margin-bottom: .125rem;
  margin-top: .125rem;
}
.fr-table-cell > .fr-icon {
  --fr-icon__size: 1rem;

  margin-bottom: .25rem;
  margin-top: .25rem;
}
.fr-table-cell--link {
  color: var(--fr-color__blue-france-sun-113-625);
}
</style>
