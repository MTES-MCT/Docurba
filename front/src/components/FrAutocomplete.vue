<script setup lang="ts">
import { computed, useTemplateRef, watch } from 'vue'
import type { Option, Options } from '@/data/Option'
import FrButton from '@/components/FrButton.vue'
import FrInput from '@/components/FrInput.vue'
import { useAttrsAndClassName } from '@/composables/useAttrsAndClassName'
import { normalize } from '@/utils/normalize'

interface Props {
  options: Options<string>
}

const {
  options = [],
} = defineProps<Props>()
const query = defineModel<string>('query', { default: '' })
const value = defineModel<string | null>('value', { default: null })
defineOptions({
  inheritAttrs: false,
})


const { attrs, className } = useAttrsAndClassName()
const field = useTemplateRef('field')

const filteredOptions = computed<Options<string>>(() => {
  if (!query.value || labels.value.includes(query.value)) {
    return options
  }

  const filteredOptions: Options<string> = []

  for (const option of options) {
    if ('value' in option) {
      if (!normalize(option.label).includes(normalizedQuery.value)) continue

      filteredOptions.push(option)

      continue
    }

    const subOptions = option.options
      .filter(({ label }) => normalize(label).includes(normalizedQuery.value))

    if (!subOptions.length) continue

    filteredOptions.push({
      label: option.label,
      options: subOptions,
    })
  }

  return filteredOptions
})
const labels = computed<Array<string>>(() => options.flatMap((option) => [
  option.label,
  ...(
    'value' in option
      ? []
      : option.options.map(({ label }) => label)
  ),
]))
const normalizedQuery = computed<string>(() => normalize(query.value))
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

watch(selectedOption, (newValue) => {
  const newQuery = newValue ? newValue.label : ''

  if (newQuery === query.value) return

  query.value = newQuery
}, { immediate: true })

defineExpose({ field })

function select(option: Option<string>) {
  query.value = option.label
  value.value = option.value

  if (!field.value || !field.value.field) return

  field.value.field.blur()
}
</script>

<template>
  <div class="fr-autocomplete"
       :class="{ [className]: !!className }">
    <FrInput v-bind="attrs"
             class="fr-autocomplete__field fr-icon--after fr-icon--after-arrow-down-s-line"
             ref="field"
             v-model:value="query" />
    <ul class="fr-autocomplete__body"
        @mousedown.prevent>
      <template v-for="option in filteredOptions"
                :key="'value' in option ? option.value : option.label">
        <li v-if="'value' in option">
          <FrButton :disabled="option.disabled"
                    sm
                    start
                    tertiary-borderless
                    @actuated="select(option)">{{ option.label }}</FrButton>
        </li>
        <template v-else>
          <li>
            <FrButton disabled
                      sm
                      start
                      tertiary-borderless>{{ option.label }}</FrButton>
          </li>
          <li v-for="subOption in option.options"
              :key="subOption.value">
            <FrButton :disabled="subOption.disabled"
                      sm
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
.fr-autocomplete {
  display: grid;
  position: relative;
}
.fr-autocomplete__body {
  background-color: var(--color-grey-1000-100);
  display: none;
  filter: drop-shadow(var(--shadow-overlap));
  left: 0;
  list-style: none;
  margin-bottom: 0;
  margin-top: 0;
  max-height: 15.25rem;
  overflow: auto;
  padding-bottom: .25rem;
  padding-left: 0;
  padding-top: .25rem;
  position: absolute;
  top: 100%;
  width: 100%;
  z-index: 1;
}
.fr-autocomplete__body li {
  display: grid;
}
.fr-autocomplete__field:focus-within + .fr-autocomplete__body {
  display: grid;
}
</style>
