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
  <div
    class="du-tag"
    :class="{ 'du-tag--sm': sm }"
  >
    <slot />
  </div>
</template>

<style>
.du-tag {
  background-color: #e3e3fd;
  border-radius: .875rem;
  color: #000091;
  display: grid;
  font-size: .875rem;
  font-weight: 500;
  line-height: 1.25rem;
  padding: .25rem .75rem;
}
.du-tag--sm {
  border-radius: .75rem;
  font-size: .75rem;
  padding: .125rem .5rem;
}
</style>
