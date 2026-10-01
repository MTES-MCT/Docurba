<template>
  <div class="du-layout-sidemenu">
    <div class="du-layout-sidemenu__menu">
      <slot
        active-class="du-layout-sidemenu__item--active"
        default-class="du-layout-sidemenu__item"
        name="menu"
      />
    </div>
    <div class="du-layout-sidemenu__body">
      <slot />
    </div>
  </div>
</template>

<style>
.du-layout-sidemenu {
  column-gap: 2.5rem;
  display: grid;
  grid-auto-columns: auto 1fr;
  grid-auto-flow: column;
  margin-left: auto;
  margin-right: auto;
  max-width: 77rem;
  padding: 1.5rem 1rem;
  width: 100%;
}
.du-layout-sidemenu__body {
  align-items: start;
  display: grid;
  row-gap: 2.5rem;
}
.du-layout-sidemenu__menu {
  align-content: start;
  display: grid;
  padding: .5rem 1.5rem .5rem .5rem;
  position: relative;
}
.du-layout-sidemenu__menu::after {
  background-color: #ddd;
  bottom: .5rem;
  content: '';
  pointer-events: none;
  position: absolute;
  right: .5rem;
  top: .5rem;
  width: .0625rem;
}
.du-layout-sidemenu__item {
  display: grid;
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.5rem;
  padding: .75rem .5rem;
  position: relative;
  text-decoration: none;
}
a.du-layout-sidemenu__item {
  color: #161616;
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
a.du-layout-sidemenu__item--active {
  color: #000091;
}
.du-layout-sidemenu__item--active::before {
  content: '';
}
</style>
