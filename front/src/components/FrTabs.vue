<script setup lang="ts">
import { computed } from 'vue'
import type { Option } from '@/data/Option'
import BaseActionable from '@/components/BaseActionable.vue'

interface Props {
  options?: Array<Option<string>>
}

const {
  options = [],
} = defineProps<Props>()
const value = defineModel<string | null>('value')

const selectedIndex = computed<number>(() => Math.max(
  0,
  options.findIndex((option) => option.value === value.value),
))
</script>

<template>
  <div class="fr-tabs">
    <ul class="fr-tabs__list">
      <li v-for="(option, index) in options"
          :key="option.value"
          role="presentation">
        <BaseActionable class="fr-tabs__tab"
                        :class="{ 'fr-tabs__tab--active': index === selectedIndex }"
                        :disabled="option.disabled"
                        @actuated="value = option.value">{{ option.label }}</BaseActionable>
      </li>
    </ul>
    <div class="fr-tabs__body">
      <div class="fr-tabs__panels"
           :style="{ '--offset': `-${selectedIndex * 100}%` }">
        <slot />
      </div>
    </div>
  </div>
</template>

<style>
.fr-tabs {
  display: grid;
}
.fr-tabs__body {
  background-color: var(--color-grey-1000-50);
  box-shadow: inset 0 -.0625rem 0 0 var(--color-grey-900-175),
              inset .0625rem 0 0 0 var(--color-grey-900-175),
              inset -.0625rem 0 0 0 var(--color-grey-900-175);
  display: grid;
  overflow: hidden;
}
.fr-tabs__list {
  box-shadow: inset 0 -.0625rem 0 0 var(--color-grey-900-175);
  column-gap: .5rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: start;
  list-style: none;
  margin-bottom: 0;
  margin-top: 0;
  overflow: auto;
  padding-left: 1rem;
  padding-right: 1rem;
}
.fr-tabs__list li {
  display: grid;
  width: max-content;
}
.fr-tabs__panels {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 100%;
  transform: translateX(var(--offset));
  transition: transform .3s;
}
.fr-tabs__panels > * {
  padding: 1rem;
}
.fr-tabs__tab {
  background-color: var(--color-blue-france-925-125);
  box-shadow: inset 0 -.0625rem 0 0 var(--color-grey-900-175);
  color: var(--color-grey-50-1000);
  cursor: pointer;
  display: grid;
  font-family: var(--font-family-sans);
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.5rem;
  padding: .5rem 1rem;
}
.fr-tabs__tab:not(.fr-tabs__tab--active):focus,
.fr-tabs__tab:not(.fr-tabs__tab--active):hover {
  background-color: var(--color-blue-france-925-125-hover);
}
.fr-tabs__tab--active {
  background-color: var(--color-grey-1000-50);
  box-shadow: inset 0 .125rem 0 0 var(--color-blue-france-sun-113-625),
              inset .0625rem 0 0 0 var(--color-grey-900-175),
              inset -.0625rem 0 0 0 var(--color-grey-900-175);
}

@media (min-width: 48rem) {
  .fr-tabs__panels > * {
    padding: 2rem;
  }
}
</style>
