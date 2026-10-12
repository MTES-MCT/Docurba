<script>
export default {
  props: {
    sm: {
      default: false,
      type: Boolean
    }
  }
}
</script>

<template>
  <ul
    class="du-list"
    :class="{ 'du-list--sm': sm }"
  >
    <slot />
  </ul>
</template>

<style>
.du-list {
  display: grid;
}
ul.du-list {
  padding-left: 0;
}
.du-list > li {
  color: #161616;
  column-gap: .5rem;
  display: grid;
  font-size: 1rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.5rem;
}
.du-list--sm > li {
  color: #666;
  font-size: .75rem;
  line-height: 1.25rem;
}
</style>
