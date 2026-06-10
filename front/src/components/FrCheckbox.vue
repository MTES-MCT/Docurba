<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useAttrsAndClassName } from '@/composables/useAttrsAndClassName'

interface Props {
  button?: boolean
  error?: boolean
  id: string
  success?: boolean
}

const {
  button = false,
  error = false,
  id,
  success = false,
} = defineProps<Props>()
const value = defineModel<boolean>('value', { default: false })
defineOptions({
  inheritAttrs: false,
})

const { attrs, className } = useAttrsAndClassName()
const field = useTemplateRef('field')

defineExpose({ field })
</script>

<template>
  <div class="fr-checkbox"
       :class="{
         'fr-checkbox--button': button,
         'fr-checkbox--error': error,
         'fr-checkbox--success': success,
         [className]: !!className,
       }">
    <input v-bind="attrs"
           class="fr-checkbox__field"
           :id="id"
           ref="field"
           type="checkbox"
           v-model="value" />
    <label class="fr-checkbox__label"
           :for="id">
      <slot />
    </label>
  </div>
</template>

<style>
.fr-checkbox {
  display: grid;
  position: relative;
}
.fr-checkbox--button {
  justify-content: start;
  padding: .5rem 1rem;
}
.fr-checkbox--button:not([disabled]):focus-within,
.fr-checkbox--button:not([disabled]):hover {
  background-color: var(--color-grey-1000-50-hover);
}
.fr-checkbox__field {
  height: 1rem;
  left: 0;
  margin: -.5rem 0 0;
  position: absolute;
  top: 50%;
  visibility: hidden;
  width: 1rem;
}
.fr-checkbox__field:checked + .fr-checkbox__label::before {
  background-color: var(--color-blue-france-sun-113-625);
  mask-composite: exclude;
  mask-image: url('@/assets/icons/check-line.svg'),
              linear-gradient(hsl(0deg 0% 0%) 0 0);
  mask-size: 100% 100%;
}
.fr-checkbox__label {
  align-items: center;
  color: var(--color-grey-50-1000);
  column-gap: .5rem;
  display: grid;
  font-family: var(--font-family-sans);
  font-size: 1rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.5rem;
}
.fr-checkbox__label::before {
  border-radius: .25rem;
  box-shadow: inset 0 0 0 .0625rem var(--color-blue-france-sun-113-625);
  content: '';
  height: 1rem;
  pointer-events: none;
  width: 1rem;
}
.fr-checkbox__label::after {
  content: '';
  cursor: pointer;
  inset: 0;
  position: absolute;
}
</style>
