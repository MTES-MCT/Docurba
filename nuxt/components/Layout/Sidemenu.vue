<script>
export default {
  props: {
    top: {
      default: '0',
      type: String
    },
    value: {
      default: () => [],
      type: Array
    }
  }
}
</script>

<template>
  <div
    class="du-layout-sidemenu"
    :style="{ '--du-layout-sidemenu__top': top }"
  >
    <div class="du-layout-sidemenu__body">
      <NuxtLink
        v-for="item, index in value"
        :key="index"
        class="du-layout-sidemenu__item"
        :class="{ 'du-layout-sidemenu__item--active': item.active }"
        :to="item.to"
      >
        {{ item.label }}
      </NuxtLink>
    </div>
  </div>
</template>

<style>
.du-layout-sidemenu {
  align-content: start;
  box-shadow: inset -.0625rem 0 0 0 #ddd;
  display: grid;
  padding-right: 1.5rem;
}
.du-layout-sidemenu__body {
  display: grid;
  position: sticky;
  top: var(--du-layout-sidemenu__top);
}
.du-layout-sidemenu__item {
  color: #161616 !important;
  display: grid;
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.5rem;
  padding: .75rem 1rem;
  position: relative;
  text-decoration: none;
}
.du-layout-sidemenu__item:focus-visible,
.du-layout-sidemenu__item:hover {
  background-color: #f6f6f6;
}
.du-layout-sidemenu__item::before {
  background-color: currentColor;
  bottom: .75rem;
  left: 0;
  pointer-events: none;
  position: absolute;
  top: .75rem;
  width: .125rem;
}
.du-layout-sidemenu__item--active {
  color: #000091 !important;
}
.du-layout-sidemenu__item--active::before {
  content: '';
}
</style>
