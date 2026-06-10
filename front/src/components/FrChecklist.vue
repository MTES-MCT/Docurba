<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import type { Option, Options } from '@/data/Option'
import BaseActionable from '@/components/BaseActionable.vue'
import FrCheckbox from '@/components/FrCheckbox.vue'
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
const selection = defineModel<Array<string>>('selection', { default: [] })
defineOptions({
  inheritAttrs: false,
})

const indexesByValue = computed<Record<string, [number, number]>>(() => {
  const indexesByValue: Record<string, [number, number]> = {}

  options.forEach((option, index) => {
    if ('value' in option) {
      indexesByValue[option.value] = [index, 0]
    } else {
      option.options.forEach((subOption, subIndex) => {
        indexesByValue[subOption.value] = [index, subIndex]
      })
    }
  })

  return indexesByValue
})
const label = computed<string>(() =>
  selection.value.length && selection.value.length < optionsCount.value
    ? selectedOptions.value.map(({ label }) => label).join(', ')
    : placeholder
)
const optionsCount = computed<number>(() => {
  let optionsCount = 0

  options.forEach((option) => {
    optionsCount += 'value' in option ? 1 : option.options.length
  })

  return optionsCount
})
const selectedByValue = computed<Record<string, boolean>>(() => {
  const selectedByValue: Record<string, boolean> = {}

  options.forEach((option) => {
    if ('value' in option) {
      selectedByValue[option.value] = selection.value.includes(option.value)

      return
    }

    option.options.forEach((subOption) => {
      selectedByValue[subOption.value] = selection.value.includes(subOption.value)
    })
  })

  return selectedByValue
})
const selectedOptions = computed<Array<Option<string>>>(() => {
  const selectedOptions: Array<Option<string>> = []

  for (const value of selection.value) {
    const indexes = indexesByValue.value[value]

    if (!indexes) continue

    const option = options[indexes[0]]

    if (!option) continue

    if ('value' in option) {
      selectedOptions.push(option)

      continue
    }

    const subOption = option.options[indexes[1]]

    if (!subOption) continue

    selectedOptions.push(subOption)
  }

  return selectedOptions
})

const { attrs, className } = useAttrsAndClassName()
const field = useTemplateRef('field')

defineExpose({ field })

function select(option: Option<string>) {
  const index = selection.value.indexOf(option.value)

  if (index === -1) {
    selection.value = [
      ...selection.value,
      option.value,
    ].sort((a, b) => {
      const aIndexes = indexesByValue.value[a]
      const bIndexes = indexesByValue.value[b]

      return !aIndexes || !bIndexes
        ? 0
        : aIndexes[0] === bIndexes[0]
          ? aIndexes[1] === bIndexes[1]
            ? 0
            : aIndexes[1] > bIndexes[1]
              ? 1
              : -1
          : aIndexes[0] > bIndexes[0]
            ? 1
            : -1
    })
  } else {
    selection.value = [
      ...selection.value.slice(0, index),
      ...selection.value.slice(index + 1),
    ]
  }
}
</script>

<template>
  <div class="fr-checklist"
       :class="{
         'fr-checklist--error': error,
         'fr-checklist--success': success,
         [className]: !!className,
       }"
       ref="element">
    <BaseActionable v-bind="attrs"
                    class="fr-checklist__field"
                    :id="id"
                    ref="field">{{ label }}</BaseActionable>
    <ul class="fr-checklist__body"
        @mousedown.prevent>
      <template v-for="option in options"
                :key="'value' in option ? option.value : option.label">
        <li v-if="'value' in option">
          <FrCheckbox button
                      :disabled="option.disabled"
                      :id="`${id}-${option.value}`"
                      :value="selectedByValue[option.value]"
                      @update:value="select(option)">{{ option.label }}</FrCheckbox>
        </li>
        <template v-else>
          <li class="fr-checkbox__label">{{ option.label }}</li>
          <li v-for="subOption in option.options"
              :key="subOption.value">
            <FrCheckbox button
                        :disabled="subOption.disabled"
                        :id="`${id}-${subOption.value}`"
                        :value="selectedByValue[subOption.value]"
                        @update:value="select(subOption)">{{ subOption.label }}</FrCheckbox>
          </li>
        </template>
      </template>
    </ul>
  </div>
</template>

<style>
.fr-checklist {
  display: grid;
  position: relative;
}
.fr-checklist:focus-within .fr-checklist__field:not([disabled]) + .fr-checklist__body {
  display: grid;
}
.fr-checklist--error .fr-checklist__field {
  box-shadow: inset 0 -.125rem 0 0 var(--color-error-425-625);
}
.fr-checklist--success .fr-checklist__field {
  box-shadow: inset 0 -.125rem 0 0 var(--color-success-425-625);
}
.fr-checklist__body {
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
.fr-checklist__body li {
  display: grid;
}
.fr-checklist__field {
  background-color: var(--color-grey-950-100);
  border-top-left-radius: .25rem;
  border-top-right-radius: .25rem;
  box-shadow: inset 0 -.125rem 0 0 var(--color-grey-200-850);
  color: var(--color-grey-200-850);
  font-family: var(--font-family-sans);
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5rem;
  overflow: hidden;
  padding: .5rem 3rem .5rem 1rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.fr-checklist__field[disabled] {
  box-shadow: inset 0 -.125rem 0 0 var(--color-grey-925-125);
  color: var(--color-grey-625-425);
  cursor: not-allowed;
}
.fr-checklist__field::after {
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
