<script setup lang="ts">
import BaseActionable from '@/components/BaseActionable.vue'

interface Props {
  active?: boolean
  icon?: boolean
  lg?: boolean
  secondary?: boolean
  sm?: boolean
  start?: boolean
  tertiary?: boolean
  tertiaryBorderless?: boolean
}

const {
  active = false,
  icon = false,
  lg = false,
  secondary = false,
  sm = false,
  start = false,
  tertiary = false,
  tertiaryBorderless = false,
} = defineProps<Props>()
</script>

<template>
  <BaseActionable class="fr-button"
                  :class="{
                    'fr-button--active': active,
                    'fr-button--icon': icon,
                    'fr-button--lg': lg,
                    'fr-button--secondary': secondary,
                    'fr-button--sm': sm,
                    'fr-button--start': start,
                    'fr-button--tertiary': tertiary,
                    'fr-button--tertiary-borderless': tertiaryBorderless,
                  }">
    <slot />
  </BaseActionable>
</template>

<style>
.fr-button {
  align-items: center;
  background-color: var(--color-blue-france-sun-113-625);
  color: var(--color-blue-france-975-sun-113);
  column-gap: .5rem;
  cursor: pointer;
  display: grid;
  font-family: var(--font-family-sans);
  font-size: 1rem;
  font-weight: 500;
  grid-auto-flow: column;
  justify-content: center;
  line-height: 1.5rem;
  min-width: 2.5rem;
  padding: .5rem 1rem;
  text-decoration: none;
}
.fr-button[disabled] {
  cursor: default;
}
.fr-button[disabled]:not(.fr-button--active) {
  background-color: var(--color-grey-925-125);
  color: var(--color-grey-625-425);
}
.fr-button:not([disabled]):focus,
.fr-button:not([disabled]):hover,
.fr-buttonh:not([disabled]).fr-button--active {
  background-color: var(--color-blue-france-sun-113-625-hover);
}
.fr-button.fr-icon--before::before {
  margin-left: -.125rem;
}
.fr-button.fr-icon--after::after {
  margin-right: -.125rem;
}
.fr-button--icon {
  height: 2.5rem;
  justify-content: start;
  overflow: hidden;
  padding-left: .5rem;
  padding-right: .5rem;
  white-space: nowrap;
  width: 2.5rem;
}
.fr-button--icon.fr-button--lg {
  height: 2.75rem;
  padding-left: .5rem;
  padding-right: .5rem;
  width: 2.75rem;
}
.fr-button--icon.fr-button--lg.fr-icon--before::before,
.fr-button--icon.fr-button--lg.fr-icon--after::after {
  margin: .125rem;
}
.fr-button--icon.fr-button--sm {
  height: 2rem;
  padding-left: .25rem;
  padding-right: .25rem;
  width: 2rem;
}
.fr-button--icon.fr-icon--before::before,
.fr-button--icon.fr-icon--after::after {
  margin: .25rem;
}
.fr-button--lg {
  font-size: 1.125rem;
  line-height: 1.75rem;
  min-width: 2.75rem;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}
.fr-button--lg.fr-icon--before::before,
.fr-button--lg.fr-icon--after::after {
  height: 1.5rem;
  width: 1.5rem;
}
.fr-button--lg.fr-icon--before::before {
  margin-left: -.1875rem;
}
.fr-button--lg.fr-icon--after::after {
  margin-right: -.1875rem;
}
.fr-button--secondary {
  background-color: transparent;
  box-shadow: inset 0 0 0 .0625rem var(--color-blue-france-sun-113-625);
  color: var(--color-blue-france-sun-113-625);
}
.fr-button--secondary[disabled]:not(.fr-button--active) {
  background-color: transparent;
  box-shadow: inset 0 0 0 .0625rem var(--color-grey-925-125);
  color: var(--color-grey-625-425);
}
.fr-button--secondary:not([disabled]):focus,
.fr-button--secondary:not([disabled]):hover,
.fr-button--secondary:not([disabled]).fr-button--active {
  background-color: var(--color-grey-1000-50-hover);
}
.fr-button--sm {
  font-size: .875rem;
  min-width: 2rem;
  padding: .25rem .75rem;
}
.fr-button--start {
  justify-content: start;
}
.fr-button--tertiary {
  background-color: transparent;
  box-shadow: inset 0 0 0 .0625rem var(--color-grey-900-175);
  color: var(--color-blue-france-sun-113-625);
}
.fr-button--tertiary[disabled]:not(.fr-button--active) {
  background-color: transparent;
  box-shadow: inset 0 0 0 .0625rem var(--color-grey-925-125);
  color: var(--color-grey-625-425);
}
.fr-button--tertiary:not([disabled]):focus,
.fr-button--tertiary:not([disabled]):hover,
.fr-button--tertiary:not([disabled]).fr-button--active {
  background-color: var(--color-grey-1000-50-hover);
}
.fr-button--tertiary-borderless {
  background-color: transparent;
  color: var(--color-blue-france-sun-113-625);
}
.fr-button--tertiary-borderless[disabled]:not(.fr-button--active) {
  background-color: transparent;
  color: var(--color-grey-625-425);
}
.fr-button--tertiary-borderless:not([disabled]):focus,
.fr-button--tertiary-borderless:not([disabled]):hover,
.fr-button--tertiary-borderless:not([disabled]).fr-button--active {
  background-color: var(--color-grey-1000-50-hover);
}
</style>
