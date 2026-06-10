<script setup lang="ts">
interface Props {
  fluid?: boolean
  tag?: string
  vertical?: boolean
}

const {
  fluid = false,
  tag = 'div',
  vertical = false,
} = defineProps<Props>()
</script>

<template>
  <component :is="tag"
             class="fr-container"
             :class="{
               'fr-container--fluid': fluid,
               'fr-container--vertical': vertical,
             }">
    <slot />
  </component>
</template>

<style>
.fr-container {
  display: grid;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
  row-gap: 1rem;
  width: 100%;
}
.fr-container--fluid {
  overflow: hidden;
  padding: 0;
}
.fr-container--vertical {
  align-content: start;
}
.fr-container--vertical:not(.fr-container--fluid) {
  padding-bottom: 2.5rem;
  padding-top: 2.5rem;
}

@media (min-width: 48rem) {
  .fr-container--fluid {
    overflow: visible;
    padding-left: 1rem;
    padding-right: 1rem;
  }
  .fr-container--vertical {
    padding-bottom: 2.5rem;
    padding-top: 2.5rem;
  }
}

@media (min-width: 62rem) {
  .fr-container {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    row-gap: 1.5rem;
  }
}

@media (min-width: 78rem) {
  .fr-container {
    max-width: 78rem;
  }
}
</style>
