<script>
export default {
  props: {
    rows: {
      default: 0,
      type: Number
    },
    value: {
      default: '',
      type: String
    }
  },
  computed: {
    document () {
      return this.value
        ? { body: this.$md.compile(this.value) }
        : undefined
    }
  }
}
</script>

<template>
  <component
    :is="document ? 'NuxtContent' : 'p'"
    class="du-text"
    :class="{
      'du-text--ellipsis': !!rows,
      'du-text--markdown': !!document
    }"
    :document="document"
    :style="{ '--du-text__rows': rows }"
    :title="rows && value ? value : undefined"
  >
    <slot />
  </component>
</template>

<style>
.du-text {
  color: #3a3a3a;
  font-size: .875rem;
  font-weight: 400;
  line-height: 1.5rem;
}
p.du-text {
  margin-bottom: 0;
}
.du-text--ellipsis {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: var(--du-text__rows);
  line-clamp: var(--du-text__rows);
  max-height: calc(var(--du-text__rows) * 1.5rem);
  overflow: hidden;
}
.du-text--markdown > *:last-child {
  margin-bottom: 0;
}
</style>
