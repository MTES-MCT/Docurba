<script>
export default {
  props: {
    rows: {
      default: '1',
      type: String
    },
    tag: {
      default: 'span',
      type: String
    }
  }
}
</script>

<template>
  <component
    :is="tag"
    class="du-ellipsis"
    :style="{ '--du-ellipsis__rows': rows }"
  >
    <slot />
  </component>
</template>

<style>
.du-ellipsis {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: var(--du-ellipsis__rows);
  line-clamp: var(--du-ellipsis__rows);
  max-height: calc(var(--du-ellipsis__rows) * 1.5rem);
  overflow: hidden;
}
</style>
