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
  <div v-if="value.length"
       class="fr-sidemenu">
    <div class="fr-sidemenu__body">
      <FRActionable v-for="item, index in value"
                    :key="index"
                    class="fr-sidemenu__item"
                    :class="{ 'fr-sidemenu__item--active': item.active }"
                    :to="item.to">
        {{ item.label }}
      </FRActionable>
    </div>
  </div>
</template>

<style>
.fr-sidemenu {
  align-content: start;
  box-shadow: inset 0 -.0625rem 0 0 var(--fr-color__grey-900-175);
  display: grid;
  padding-bottom: 1rem;
}
.fr-sidemenu__body {
  display: grid;
}
.fr-sidemenu__item {
  color: var(--fr-color__grey-50-1000);
  display: grid;
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.5rem;
  padding: .75rem 1rem;
  position: relative;
  text-decoration: none;
}
.fr-sidemenu__item:focus-visible,
.fr-sidemenu__item:hover {
  background-color: var(--fr-color__grey-1000-50--hover);
}
.fr-sidemenu__item::before {
  bottom: .75rem;
  content: '';
  left: 0;
  position: absolute;
  top: .75rem;
  width: .125rem;
}
.fr-sidemenu__item--active {
  color: var(--fr-color__blue-france-sun-113-625);
}
.fr-sidemenu__item--active::before {
  background-color: currentColor;
}

@media (min-width: 48rem) {
  .fr-sidemenu {
    box-shadow: inset -.0625rem 0 0 0 var(--fr-color__grey-900-175);
    padding-bottom: 0;
    padding-right: 1rem;
  }
  .fr-sidemenu__body {
    position: sticky;
    top: var(--fr-header__size);
  }
}

@media (min-width: 62rem) {
  .fr-sidemenu {
    padding-right: 1.5rem;
  }
}
</style>
