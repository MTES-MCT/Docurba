<script>
export default {
  props: {
    value: {
      default: () => [],
      type: Array,
    },
  },
}
</script>

<template>
  <div class="fr-tabs">
    <div class="fr-tabs__header">
      <FRActionable v-for="item, index in value"
                    :key="index"
                    class="fr-tabs__tab"
                    :class="{ 'fr-tabs__tab--active': item.active }"
                    :to="item.to">
        {{ item.label }}
      </FRActionable>
    </div>
    <div class="fr-tabs__body">
      <slot />
    </div>
  </div>
</template>

<style>
.fr-tabs {
  display: grid;
}
.fr-tabs__body {
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: inset 0 0 0 .0625rem var(--fr-color__grey-900-175);
  padding: 1rem;
}
.fr-tabs__header {
  column-gap: .5rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: start;
  padding-left: 1rem;
  padding-right: 1rem;
}
.fr-tabs__tab {
  background-color: var(--fr-color__blue-france-925-125);
  color: var(--fr-color__grey-50-1000);
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.5rem;
  padding: .5rem 1rem;
  text-decoration: none;
}
.fr-tabs__tab:not(.fr-tabs__tab--active):focus-visible,
.fr-tabs__tab:not(.fr-tabs__tab--active):hover {
  background-color: var(--fr-color__blue-france-925-125--hover);
}
.fr-tabs__tab--active {
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: inset 0 .125rem 0 0 var(--fr-color__blue-france-sun-113-625),
              inset .0625rem 0 0 0 var(--fr-color__grey-900-175),
              inset -.0625rem 0 0 0 var(--fr-color__grey-900-175),
              inset 0 -.0625rem 0 0 var(--fr-color__grey-1000-50);
  color: var(--fr-color__blue-france-sun-113-625);
  margin-bottom: -.0625rem;
  padding-bottom: .5625rem;
  position: relative;
}

@media (min-width: 62rem) {
  .fr-tabs__body {
    padding: 1.5rem;
  }
  .fr-tabs__header {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
}
</style>
