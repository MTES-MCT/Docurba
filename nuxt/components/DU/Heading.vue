<script>
export default {
  props: {
    ellipsis: {
      default: false,
      type: Boolean
    },
    level: {
      default: 2,
      type: Number
    },
    strong: {
      default: false,
      type: Boolean
    }
  },
  computed: {
    element () {
      return `h${this.level}`
    }
  }
}
</script>

<template>
  <component
    :is="element"
    class="du-heading"
    :class="{
      'du-heading--ellipsis': ellipsis,
      'du-heading--strong': strong
    }"
  >
    <slot />
  </component>
</template>

<style>
.du-heading--ellipsis {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
h2.du-heading {
  color: #000 !important;
  font-size: 2rem;
  font-weight: 700;
  line-height: 2.5rem;
}
h3.du-heading {
  color: #161616 !important;
  font-size: 1.5rem;
  font-weight: 400;
  line-height: 2rem;
}
h3.du-heading strong {
  font-weight: 700;
}
h3.du-heading--strong {
  font-size: 1.25rem;
  font-weight: 800;
  line-height: 1.75rem;
}
h4.du-heading,
h5.du-heading {
  color: #3a3a3a !important;
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.5rem;
}
h4.du-heading--strong {
  font-weight: 700;
}
</style>
