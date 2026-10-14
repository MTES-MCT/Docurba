<template>
  <div class="du-tabs">
    <slot active-class="du-tabs__tab--active" />
  </div>
</template>

<style>
.du-tabs {
  border-radius: .25rem;
  box-shadow: inset 0 0 0 .0625rem #ddd;
  display: grid;
  grid-auto-flow: column;
  justify-content: start;
}
.du-tabs a {
  color: #161616 !important;
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
.du-tabs a:not(.du-tabs__tab--active):focus-visible,
.du-tabs a:not(.du-tabs__tab--active):hover {
  background-image: linear-gradient(#f6f6f6, #f6f6f6);
  background-size: calc(100% - .5rem) calc(100% - .5rem);
  background-position: center;
}
.du-tabs a.du-tabs__tab--active {
  border-radius: .25rem;
  box-shadow: inset 0 0 0 .0625rem #000091;
  color: #000091 !important;
}
.du-tabs .v-icon {
  color: inherit;
  margin: .25rem -.25rem;
}
</style>
