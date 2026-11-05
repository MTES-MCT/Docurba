<script>
import { mdiChevronDown } from '@mdi/js'
import { orderBy } from 'lodash'

export default {
  props: {
    error: {
      default: false,
      type: Boolean,
    },
    id: {
      default: undefined,
      type: String,
    },
    options: {
      default: () => [],
      type: Array,
    },
    placeholder: {
      default: undefined,
      type: String,
    },
    success: {
      default: false,
      type: Boolean,
    },
    value: {
      default: () => [],
      type: Array,
    },
  },
  data() {
    return {
      active: false,
      icons: {
        mdiChevronDown,
      },
    }
  },
  computed: {
    label() {
      return this.value.length && this.value.length < this.options.length
        ? this.value.map((value) => {
          const option = this.options.find((option) => option.value === value)

          return option ? option.label : value
        }).join(', ')
        : this.placeholder
    },
    values() {
      return this.options.map(({ value }) => value)
    },
  },
  mounted() {
    document.documentElement.addEventListener('click', this.clickListener)
  },
  destroyed() {
    document.documentElement.removeEventListener('click', this.clickListener)
  },
  methods: {
    clickListener(event) {
      if (
        this.active
        && this.$el
        && this.$el !== event.target
        && !this.$el.contains(event.target)
      ) {
        this.active = false
      }
    },
    toggle(option) {
      const index = this.value.indexOf(option.value)
      let updatedValue = []

      if (index === -1) {
        if (!this.value.length) {
          const optionIndex = this.values.indexOf(option.value)
          updatedValue = [
            ...this.values.slice(0, optionIndex),
            ...this.values.slice(optionIndex + 1),
          ]
        } else if (this.value.length < this.options.length - 1) {
          updatedValue = orderBy(
            [...this.value, option.value],
            (value) => this.values.indexOf(value),
          )
        }
      } else {
        updatedValue = [
          ...this.value.slice(0, index),
          ...this.value.slice(index + 1),
        ]
      }

      this.$emit('input', updatedValue)
    },
  },
}
</script>

<template>
  <FRField class="fr-field-multiselect"
           :class="{ 'fr-field-multiselect--active': active }"
           :error="error"
           :icon="icons.mdiChevronDown"
           :id="id"
           :success="success">
    <template #default>
      <slot />
    </template>
    <template #hint>
      <slot name="hint" />
    </template>
    <template #input>
      <input class="fr-field__input"
             :id="id"
             :placeholder="placeholder"
             readonly
             :title="label === placeholder ? undefined : label"
             :value="label === placeholder ? '' : label"
             @click="active = !active"
             @keydown.enter="active = !active"
             @keydown.space="active = !active" />
      <div class="fr-field-multiselect__body">
        <FRActionable v-for="option in options"
                      :key="option.value"
                      class="fr-field-multiselect__item"
                      :class="{ 'fr-field-multiselect__item--active': !value.length || value.includes(option.value) }"
                      :disabled="option.disabled"
                      @actuated="toggle(option)">
          <slot name="option"
                :value="option.value">
            {{ option.label }}
          </slot>
        </FRActionable>
      </div>
    </template>
    <template #description>
      <slot name="description" />
    </template>
  </FRField>
</template>

<style>
.fr-field-multiselect--active > .fr-field__body > .fr-field-multiselect__body {
  visibility: visible;
}
.fr-field-multiselect--active > .fr-field__body > .fr-icon {
  transform: rotate(180deg);
}
.fr-field-multiselect__body {
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: var(--fr-shadow__raised);
  display: grid;
  left: 0;
  max-height: 18.75rem;
  min-width: 100%;
  overflow: auto;
  position: absolute;
  top: 100%;
  visibility: hidden;
  z-index: var(--fr-index__menu);
}
.fr-field-multiselect__item {
  align-items: center;
  color: var(--fr-color__grey-200-850);
  column-gap: .5rem;
  cursor: pointer;
  display: grid;
  font-size: .875rem;
  grid-auto-flow: column;
  justify-content: start;
  line-height: 1.5rem;
  padding: .5rem 1rem;
  text-decoration: none;
}
.fr-field-multiselect__item:focus-visible,
.fr-field-multiselect__item:hover {
  background-color: var(--fr-color__grey-1000-50--hover);
}
.fr-field-multiselect__item[disabled] {
  color: var(--fr-color__grey-425-625);
  cursor: not-allowed;
}
.fr-field-multiselect__item::before {
  content: '';
  border-radius: .25rem;
  box-shadow: inset 0 0 0 .0625rem var(--fr-color__blue-france-sun-113-625);
  height: 1rem;
  margin-bottom: .25rem;
  margin-top: .25rem;
  width: 1rem;
}
.fr-field-multiselect__item--active::before {
  background-color: var(--fr-color__blue-france-sun-113-625);
  mask-composite: exclude;
  mask-image: url('data:image/svg+xml;charset=utf-8,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"%3E%3Cpath fill="%23000000" d="m10 15.17 9.2-9.2 1.4 1.42L10 18l-6.36-6.36 1.4-1.42z"/%3E%3C/svg%3E'),
              linear-gradient(#fff 0 0);
}
</style>
