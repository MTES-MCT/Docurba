<script>
export default {
  props: {
    disabled: {
      default: false,
      type: Boolean,
    },
    to: {
      default: undefined,
      type: [String, Object],
    },
  },
  computed: {
    external() {
      return (
        !this.disabled &&
        typeof this.to === 'string' &&
        this.to.startsWith('http')
      )
    },
    href() {
      return typeof this.to === 'string' ? this.to : undefined
    },
  },
  methods: {
    actuate(event) {
      if (this.disabled) return

      this.$emit('actuated', event)
    }
  },
}
</script>

<template>
  <a v-if="external"
     :href="href"
     rel="noopener noreferrer"
     target="_blank">
    <slot />
  </a>
  <NuxtLink v-else-if="!disabled && to"
            :to="to">
    <slot />
  </NuxtLink>
  <div v-else
       :disabled="disabled ? true : undefined"
       :tabindex="disabled ? undefined : '0'"
       @click="actuate($event)"
       @keydown.enter="actuate($event)"
       @keydown.space="actuate($event)">
    <slot />
  </div>
</template>
