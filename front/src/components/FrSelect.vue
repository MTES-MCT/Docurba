<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import type { Option, Options } from '@/data/Option'
import BaseActionable from '@/components/BaseActionable.vue'
import FrButton from '@/components/FrButton.vue'
import { useAttrsAndClassName } from '@/composables/useAttrsAndClassName'

interface Props {
  error?: boolean | string
  id: string
  options?: Options<string>
  placeholder?: string
  success?: boolean | string
}

const {
  error = false,
  id,
  options = [],
  placeholder = '',
  success = false,
} = defineProps<Props>()
const value = defineModel<string>('value', { default: '' })
defineOptions({
  inheritAttrs: false,
})

const selectedOption = computed<Option<string> | null>(() => {
  for (const option of options) {
    if ('value' in option) {
      if (option.value !== value.value) continue

      return option
    }
    for (const subOption of option.options) {
      if (subOption.value !== value.value) continue

      return subOption
    }
  }

  return null
})

const { attrs, className } = useAttrsAndClassName()
const field = useTemplateRef('field')

defineExpose({ field })

function select(option: Option<string>) {
  value.value = option.value

  if (!field.value || !field.value.$el) return

  field.value.$el.blur()
}
</script>

<template>
  <div class="fr-select"
       :class="{
         'fr-select--error': error,
         'fr-select--success': success,
         [className]: !!className,
       }"
       ref="element">
    <BaseActionable v-bind="attrs"
                    class="fr-select__field"
                    :id="id"
                    ref="field">{{ selectedOption ? selectedOption.label : placeholder }}</BaseActionable>
    <ul class="fr-select__body"
        @mousedown.prevent>
      <template v-for="option in options"
                :key="'value' in option ? option.value : option.label">
        <li v-if="'value' in option">
          <FrButton :disabled="option.disabled"
                    start
                    tertiary-borderless
                    @actuated="select(option)">{{ option.label }}</FrButton>
        </li>
        <template v-else>
          <li>
            <FrButton disabled
                      start
                      tertiary-borderless>{{ option.label }}</FrButton>
          </li>
          <li v-for="subOption in option.options"
              :key="subOption.value">
            <FrButton :disabled="subOption.disabled"
                      start
                      tertiary-borderless
                      @actuated="select(subOption)">{{ subOption.label }}</FrButton>
          </li>
        </template>
      </template>
    </ul>
  </div>
</template>

<style>
.fr-select {
  display: grid;
  position: relative;
}
.fr-select:focus-within .fr-select__field:not([disabled]) + .fr-select__body {
  display: grid;
}
.fr-select--error .fr-select__field {
  box-shadow: inset 0 -.125rem 0 0 var(--color-error-425-625);
}
.fr-select--success .fr-select__field {
  box-shadow: inset 0 -.125rem 0 0 var(--color-success-425-625);
}
.fr-select__body {
  background-color: var(--color-grey-1000-100);
  display: none;
  filter: drop-shadow(var(--shadow-overlap));
  left: 0;
  list-style: none;
  margin-bottom: 0;
  margin-top: 0;
  max-height: 14.25rem;
  overflow: auto;
  padding-bottom: .5rem;
  padding-left: 0;
  padding-top: .5rem;
  position: absolute;
  top: 100%;
  width: 100%;
  z-index: 1;
}
.fr-select__body li {
  display: grid;
}
.fr-select__field {
  background-color: var(--color-grey-950-100);
  border-top-left-radius: .25rem;
  border-top-right-radius: .25rem;
  box-shadow: inset 0 -.125rem 0 0 var(--color-grey-200-850);
  color: var(--color-grey-200-850);
  display: grid;
  font-family: var(--font-family-sans);
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5rem;
  min-height: 2.5rem;
  overflow: hidden;
  padding: .5rem 3rem .5rem 1rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.fr-select__field[disabled] {
  box-shadow: inset 0 -.125rem 0 0 var(--color-grey-925-125);
  color: var(--color-grey-625-425);
  cursor: not-allowed;
}
.fr-select__field::after {
  background-color: currentColor;
  content: '';
  height: 1rem;
  margin-top: -.5rem;
  mask-image: url('@/assets/icons/arrow-down-s-line.svg');
  mask-size: 100% 100%;
  pointer-events: none;
  position: absolute;
  top: 50%;
  right: 1rem;
  width: 1rem;
}
</style>
