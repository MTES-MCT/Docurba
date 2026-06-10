<script setup lang="ts">
import type { ClassValue } from 'vue'
import { computed } from 'vue'
import type { RouteLocationRaw } from 'vue-router'

interface Props {
  close?: boolean
  icon?: string | null
  iconLeft?: boolean
  iconRight?: boolean
  lg?: boolean
  menu?: boolean
  secondary?: boolean
  sm?: boolean
  tertiary?: boolean
  tertiaryNoOutline?: boolean
  to?: RouteLocationRaw | null
}

const {
  close = false,
  icon = null,
  iconLeft = false,
  iconRight = false,
  lg = false,
  menu = false,
  secondary = false,
  sm = false,
  tertiary = false,
  tertiaryNoOutline = false,
  to = null,
} = defineProps<Props>()

const elementClass = computed<ClassValue>(() => ({
  'fr-btn--close': close,
  'fr-btn--icon-left': iconLeft,
  'fr-btn--icon-right': iconRight,
  'fr-btn--lg': lg,
  'fr-btn--menu': menu,
  'fr-btn--secondary': secondary,
  'fr-btn--sm': sm,
  'fr-btn--tertiary': tertiary,
  'fr-btn--tertiary-no-outline': tertiaryNoOutline,
  [`fr-icon-${icon}`]: !!icon,
}))
const external = computed<boolean>(() =>
  typeof to === 'string' && to.startsWith('http')
)
</script>

<template>
  <RouterLink v-if="to"
              class="fr-btn"
              :class="elementClass"
              :rel="external ? 'noopener' : undefined"
              :to="to">
    <slot />
  </RouterLink>
  <button v-else
          class="fr-btn"
          :class="elementClass"
          type="button">
    <slot />
  </button>
</template>
