<script>
export default {
  props: {
    disabled: {
      default: false,
      type: Boolean
    },
    to: {
      default: undefined,
      type: [String, Object]
    }
  },
  computed: {
    external () {
      return (
        !this.disabled &&
        typeof this.to === 'string' &&
        this.to.startsWith('http')
      )
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
  <a
    v-if="external"
    :class="elementClass"
    :href="to"
    rel="noopener noreferrer"
    target="_blank"
  >
    <slot />
  </a>
  <NuxtLink
    v-else-if="!disabled && to"
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
