<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useAttrsAndClassName } from '@/composables/useAttrsAndClassName'

interface Props {
  error?: boolean
  success?: boolean
}

const {
  error = false,
  success = false,
} = defineProps<Props>()
const value = defineModel<string>('value', { default: '' })
defineOptions({
  inheritAttrs: false,
})

const { attrs, className } = useAttrsAndClassName()
const field = useTemplateRef('field')

defineExpose({ field })
</script>

<template>
  <div class="fr-input"
       :class="{
         'fr-input--error': error,
         'fr-input--success': success,
         [className]: !!className,
       }">
    <input v-bind="attrs"
           class="fr-input__field"
           ref="field"
           v-model="value" />
  </div>
</template>

<style>
.fr-input {
  color: var(--color-grey-200-850);
  display: grid;
  position: relative;
}
.fr-input.fr-icon--after::after {
  position: absolute;
  right: 1rem;
  top: .75rem;
}
.fr-input.fr-icon--after .fr-input__field {
  padding-right: 3rem;
}
.fr-input--error .fr-input__field {
  box-shadow: inset 0 -.125rem 0 0 var(--color-error-425-625);
}
.fr-input--success .fr-input__field {
  box-shadow: inset 0 -.125rem 0 0 var(--color-success-425-625);
}
.fr-input__field {
  background-color: var(--color-grey-950-100);
  border: none;
  border-top-left-radius: .25rem;
  border-top-right-radius: .25rem;
  box-shadow: inset 0 -.125rem 0 0 var(--color-grey-200-850);
  color: inherit;
  display: block;
  font-family: var(--font-family-sans);
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5rem;
  padding: .5rem 1rem;
  width: 100%;
}
.fr-input__field[disabled] {
  box-shadow: inset 0 -.125rem 0 0 var(--color-grey-925-125);
  color: var(--color-grey-625-425);
  cursor: not-allowed;
}
</style>
