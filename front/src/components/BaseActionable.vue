<script setup lang="ts">
import { computed } from 'vue'
import type { RouteLocationRaw } from 'vue-router'

interface Emit {
  actuated: [event: KeyboardEvent | MouseEvent | PointerEvent]
}
interface Props {
  disabled?: boolean
  to?: string | RouteLocationRaw | null
}

const emit = defineEmits<Emit>()
const {
  disabled = false,
  to = null,
} = defineProps<Props>()

const external = computed<boolean>(() =>
  !disabled
  && !!to
  && typeof to === 'string'
  && to.startsWith('http')
)

function actuate(event: KeyboardEvent | MouseEvent | PointerEvent) {
  if (disabled) return

  emit('actuated', event)
}
</script>

<template>
  <a v-if="external"
     :href="to as string"
     rel="noopener noreferrer"
     target="_blank">
    <slot />
  </a>
  <RouterLink v-else-if="!disabled && to"
              active-class="fr-link--active"
              exact-active-class="fr-link--exact-active"
              :to="to">
    <slot />
  </RouterLink>
  <div v-else
       :disabled="disabled ? true : undefined"
       :tabindex="disabled ? undefined : '0'"
       @click="actuate($event)"
       @keydown.enter="actuate($event)"
       @keydown.space="actuate($event)">
    <slot />
  </div>
</template>
