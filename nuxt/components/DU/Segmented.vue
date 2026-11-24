<template>
  <div class="du-segmented">
    <slot active-class="du-segmented__item--active" />
  </div>
</template>

<style>
.du-segmented {
  border-radius: .25rem;
  box-shadow: inset 0 0 0 .0625rem #ddd;
  display: grid;
  grid-auto-flow: column;
  justify-content: start;
}
.du-segmented a {
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
.du-segmented a:not(.du-segmented__item--active):focus-visible,
.du-segmented a:not(.du-segmented__item--active):hover {
  background-image: linear-gradient(#f6f6f6, #f6f6f6);
  background-size: calc(100% - .5rem) calc(100% - .5rem);
  background-position: center;
}
.du-segmented a.du-segmented__item--active {
  border-radius: .25rem;
  box-shadow: inset 0 0 0 .0625rem #000091;
  color: #000091 !important;
}
.du-segmented .v-icon {
  color: inherit;
  margin: .25rem -.25rem;
}
</style>
