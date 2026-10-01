<template>
  <div class="du-dotted-list">
    <slot />
  </div>
</template>

<style>
.du-dotted-list {
  column-gap: .5rem;
  display: grid;
  grid-auto-flow: column;
}
.du-dotted-list a {
  box-shadow: inset 0 -.0625rem 0 0 currentColor;
  color: #000091;
  font-weight: 500;
  text-decoration: none;
}
.du-dotted-list div {
  color: #161616;
  column-gap: .5rem;
  display: grid;
  font-size: 1rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.5rem;
}
.du-dotted-list div:not(:last-child):after {
  content: '•';
  font-size: .875rem;
}
</style>
