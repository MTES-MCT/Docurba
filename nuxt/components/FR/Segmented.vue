<script>
export default {}
</script>

<template>
  <div class="fr-segmented">
    <slot active-class="fr-segmented__tab--active" />
  </div>
</template>

<style>
.fr-segmented {
  background-color: var(--fr-color__grey-1000-50);
  border-radius: .25rem;
  box-shadow: inset 0 0 0 .0625rem var(--fr-color__grey-900-175);;
  display: grid;
  grid-auto-flow: column;
}
.fr-segmented > a {
  border-radius: .25rem;
  color: var(--fr-color__grey-50-1000);
  column-gap: .75rem;
  cursor: pointer;
  display: grid;
  font-size: 1rem;
  font-weight: 500;
  grid-auto-flow: column;
  line-height: 1.5rem;
  padding: .5rem 1rem;
  text-decoration: none;
}
.fr-segmented > a:not(.fr-segmented__tab--active):focus-visible,
.fr-segmented > a:not(.fr-segmented__tab--active):hover {
  background-image: linear-gradient(
    var(--fr-color__grey-1000-50--hover),
    var(--fr-color__grey-1000-50--hover)
  );
  background-size: calc(100% - .5rem) calc(100% - .5rem);
  background-position: center;
}
.fr-segmented > a.fr-segmented__tab--active {
  box-shadow: inset 0 0 0 .0625rem var(--fr-color__blue-france-sun-113-625);
  color: var(--fr-color__blue-france-sun-113-625);
}
.fr-segmented > a > .fr-icon {
  --fr-icon__size: 1rem;

  margin: .25rem -.25rem;
}
</style>
