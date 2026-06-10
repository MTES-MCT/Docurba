<script setup lang="ts">
import type { Option } from '@/data/Option'

interface Props {
  id: string
  options: Array<Option<string>>
}

const {
  id,
  options,
} = defineProps<Props>()
const value = defineModel<string>('value', { default: '' })
</script>

<template>
  <div class="fr-segmented">
    <div v-for="option in options"
         :key="option.value"
         class="fr-segmented__element">
      <input :id="`${id}-${option.value}`"
             :name="id"
             type="radio"
             :value="option.value"
             v-model="value" />
      <slot :id="`${id}-${option.value}`"
            name="label"
            :option="option">
        <label :for="`${id}-${option.value}`">{{ option.label }}</label>
      </slot>
    </div>
  </div>
</template>

<style>
.fr-segmented {
  border-radius: .25rem;
  box-shadow: inset 0 0 0 1px var(--color-grey-900-175);
  display: grid;
  grid-auto-flow: column;
  width: fit-content;
}
.fr-segmented input {
  border-radius: .25rem;
  cursor: pointer;
  height: 100%;
  inset: 0;
  margin: 0;
  opacity: 0;
  position: absolute;
  width: 100%;
}
.fr-segmented input:not(:checked):focus + label,
.fr-segmented input:not(:checked):hover + label {
  background-color: var(--color-grey-1000-50-hover);
  mask-image: linear-gradient(0deg,#fff,#fff),
              linear-gradient(0deg,#fff,#fff),
              url("data:image/svg+xml;charset=uft8,<svg xmlns='http://www.w3.org/2000/svg' width='4px' height='4px' viewBox='0 0 4 4'><circle fill='%23fff' r='2' cx='2' cy='2' /></svg>"),
              url("data:image/svg+xml;charset=uft8,<svg xmlns='http://www.w3.org/2000/svg' width='4px' height='4px' viewBox='0 0 4 4'><circle fill='%23fff' r='2' cx='2' cy='2' /></svg>"),
              url("data:image/svg+xml;charset=uft8,<svg xmlns='http://www.w3.org/2000/svg' width='4px' height='4px' viewBox='0 0 4 4'><circle fill='%23fff' r='2' cx='2' cy='2' /></svg>"),
              url("data:image/svg+xml;charset=uft8,<svg xmlns='http://www.w3.org/2000/svg' width='4px' height='4px' viewBox='0 0 4 4'><circle fill='%23fff' r='2' cx='2' cy='2' /></svg>");
  mask-position: .25rem .375rem,
                 .375rem .25rem,
                 .25rem .25rem,
                 calc(100% - .25rem) .25rem,
                 .25rem calc(100% - .25rem),
                 calc(100% - .25rem) calc(100% - .25rem);
  mask-repeat: no-repeat;
  mask-size: calc(100% - .5rem) calc(100% - .75rem),
             calc(100% - .75rem) calc(100% - .5rem),
             .25rem .25rem,
             .25rem .25rem,
             .25rem .25rem,
             .25rem .25rem;
}
.fr-segmented input:checked + label {
  box-shadow: inset 0 0 0 1px var(--color-blue-france-sun-113-625);
  color: var(--color-blue-france-sun-113-625);
}
.fr-segmented label {
  align-items: center;
  border-radius: .25rem;
  color: var(--color-grey-50-1000);
  column-gap: .5rem;
  cursor: pointer;
  display: grid;
  font-family: var(--font-family-sans);
  font-size: 1rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.5rem;
  padding: .5rem 1rem;
}
.fr-segmented__element {
  border-radius: .25rem;
  display: grid;
  position: relative;
}
</style>
