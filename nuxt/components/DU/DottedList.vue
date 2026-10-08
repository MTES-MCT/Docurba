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
    class="du-dotted-list"
    :class="{ 'du-dotted-list--sm': sm }"
  >
    <slot />
  </ul>
</template>

<style>
.du-dotted-list {
  column-gap: .5rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: start;
}
ul.du-dotted-list {
  padding-left: 0;
}
.du-dotted-list > li {
  color: #161616;
  display: grid;
  font-size: 1rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.5rem;
}
.du-dotted-list > li:not(:last-child):after {
  content: '•';
  font-size: .875rem;
  margin-left: .5rem;
}
.du-dotted-list--sm > li {
  color: #666;
  font-size: .75rem;
  line-height: 1.25rem;
}
</style>
