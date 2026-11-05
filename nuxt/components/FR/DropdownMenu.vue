<script>
export default {
  props: {
    end: {
      default: false,
      type: Boolean,
    },
    items: {
      default: () => [],
      type: Array,
    },
  },
}
</script>

<template>
  <div class="fr-dropdown-menu"
       :class="{ 'fr-dropdown-menu--end': end }">
    <slot />
    <div class="fr-dropdown-menu__body">
      <component v-for="item, index in items"
                 :key="index"
                 :is="item.action || item.to ? 'FRActionable' : 'FRText'"
                 class="fr-dropdown-menu__item"
                 :mention="(!item.action && !item.to) || undefined"
                 :to="item.to"
                 :xs="(!item.action && !item.to) || undefined"
                 @actuated="item.action && item.action($event)">
        {{ item.label }}
      </component>
    </div>
  </div>
</template>

<style>
.fr-dropdown-menu {
  display: grid;
  position: relative;
}
.fr-dropdown-menu:focus-within .fr-dropdown-menu__body,
.fr-dropdown-menu:hover .fr-dropdown-menu__body {
  visibility: visible;
}
.fr-dropdown-menu--end .fr-dropdown-menu__body {
  left: auto;
  right: 0;
}
.fr-dropdown-menu__body {
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: var(--fr-shadow__raised);
  display: grid;
  left: 0;
  min-width: 12.5rem;
  position: absolute;
  top: 100%;
  visibility: hidden;
  width: max-content;
  z-index: var(--fr-index__menu);
}
.fr-dropdown-menu__item {
  padding: .5rem 1rem;
}
a.fr-dropdown-menu__item,
.fr-dropdown-menu__item[tabindex] {
  color: var(--fr-color__blue-france-sun-113-625);
  cursor: pointer;
  font-size: .875rem;
  text-decoration: none;
}
a.fr-dropdown-menu__item:focus-visible,
a.fr-dropdown-menu__item:hover,
.fr-dropdown-menu__item[tabindex]:focus-visible,
.fr-dropdown-menu__item[tabindex]:hover {
  background-color: var(--fr-color__grey-1000-50--hover);
}
</style>
