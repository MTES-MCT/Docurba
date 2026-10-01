<script>
export default {
  props: {
    disabled: {
      default: false,
      type: Boolean
    },
    to: {
      default: null,
      type: [String, Object]
    }
  },
  methods: {
    actuate (event) {
      if (!this.disabled) {
        this.$emit('actuated', event)
      }
    }
  }
}
</script>

<template>
  <NuxtLink
    v-if="!disabled && to"
    :class="elementClass"
    :to="to"
  >
    <slot />
  </NuxtLink>
  <div
    v-else
    :class="elementClass"
    :disabled="disabled ? true : undefined"
    :tabindex="disabled ? undefined : '0'"
    @click="actuate($event)"
    @keydown.enter="actuate($event)"
    @keydown.space="actuate($event)"
  >
    <slot />
  </div>
</template>
