<script>
import { mdiChevronDown } from '@mdi/js'

export default {
  props: {
    error: {
      default: false,
      type: Boolean,
    },
    groupsOrder: {
      default: () => [],
      type: Array,
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
      default: '',
      type: String,
    },
  },
  data () {
    return {
      active: false,
      icons: {
        mdiChevronDown
      },
      query: '',
    }
  },
  computed: {
    availableOptions() {
      if (
        (this.selectedOption && this.selectedOption.label === this.query)
        || this.query === ''
      ) {
        return this.options
      }

      const searchableQuery = this.query.toLowerCase()
        .normalize('NFKD')
        .replaceAll(/[^a-z0-9]/g, '')

      return searchableQuery === ''
        ? this.options
        : this.options.filter((_, index) => this.searchableValues[index].includes(searchableQuery))
    },
    groupedOptions() {
      const groupedOptions = [{
        label: '',
        options: [],
      }, ...this.groupsOrder.map((label) => ({
        label,
        options: [],
      }))]
      const groupIndexByLabel = {
        '': 0,
        ...Object.fromEntries(this.groupsOrder.map((label, index) => [
          label,
          index + 1,
        ])),
      }

      this.availableOptions.forEach((option) => {
        const label = option.group || ''

        if (label in groupIndexByLabel) {
          groupedOptions[groupIndexByLabel[label]].options.push(option)
        } else {
          groupIndexByLabel[label] = groupedOptions.length
          groupedOptions.push({
            label,
            options: [option],
          })
        }
      })

      return groupedOptions.filter(({ options }) => options.length)
    },
    searchableValues() {
      return this.options.map(({ label }) =>
        label.toLowerCase().normalize('NFKD').replaceAll(/[^a-z0-9]/g, '')
      )
    },
    selectedOption() {
      return this.options.find((option) => option.value === this.value)
    },
  },
  watch: {
    query(newValue, oldValue) {
      if (
        !this.active
        && this.selectedOption
        && newValue !== this.selectedOption.label
        && oldValue === this.selectedOption.label
      ) {
        this.active = true
      }
    },
    selectedOption: {
      handler(value) {
        if (!value || value.label === this.query) return

        this.query = value.label
      },
      immediate: true,
    },
  },
  methods: {
    blur() {
      this.query = this.selectedOption
        ? this.selectedOption.label
        : ''
      this.active = false
    },
    focus() {
      this.active = true
    },
    select(option) {
      this.$emit('input', option.value)
      this.active = false
    },
  },
}
</script>

<template>
  <FRField :error="error"
           :id="id"
           :success="success">
    <template #label>
      <slot name="label" />
    </template>
    <template #hint>
      <slot name="hint" />
    </template>
    <template #input>
      <div class="fr-field-autocomplete"
           :class="{ 'fr-field-autocomplete--active': active }">
        <input class="fr-field__input"
               :id="id"
               :placeholder="placeholder"
               v-model="query"
               @blur="blur()"
               @focus="focus()" />
        <FRIcon :value="icons.mdiChevronDown" />
        <div class="fr-field-autocomplete__body">
          <div v-for="group in groupedOptions"
               :key="group.label"
               class="fr-field-autocomplete__group">
            <FRText v-if="group.label"
                    class="fr-field-autocomplete__item"
                    mention
                    xs>{{ group.label }}</FRText>
            <FRActionable v-for="option in group.options"
                          :key="option.value"
                          class="fr-field-autocomplete__item"
                          :class="{ 'fr-field-autocomplete__item--active': option.value === value }"
                          :disabled="option.disabled"
                          @mousedown.native.prevent
                          @actuated.prevent="select(option)">
              {{ option.label }}
            </FRActionable>
          </div>
        </div>
      </div>
    </template>
    <template #description>
      <slot name="description" />
    </template>
  </FRField>
</template>

<style>
.fr-field-autocomplete {
  display: grid;
  position: relative;
  width: 100%;
}
.fr-field-autocomplete > .fr-field__input {
  padding-right: 2.5rem;
}
.fr-field-autocomplete > .fr-icon {
  color: var(--fr-color__grey-200-850);
  pointer-events: none;
  position: absolute;
  right: .5rem;
  top: .5rem;
}
.fr-field-autocomplete--active > .fr-field-autocomplete__body {
  visibility: visible;
}
.fr-field-autocomplete--active > .fr-icon {
  transform: rotate(180deg);
}
.fr-field-autocomplete__body {
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: var(--fr-shadow__raised);
  display: grid;
  left: 0;
  max-height: 18.75rem;
  overflow: auto;
  position: absolute;
  right: 0;
  top: 100%;
  visibility: hidden;
  z-index: var(--fr-index__menu);
}
.fr-field-autocomplete__group {
  box-shadow: inset 0 -.0625rem 0 0 var(--fr-color__grey-900-175);
  display: grid;
}
.fr-field-autocomplete__item {
  padding: .5rem 1rem;
}
a.fr-field-autocomplete__item,
.fr-field-autocomplete__item[disabled],
.fr-field-autocomplete__item[tabindex] {
  font-size: .875rem;
}
a.fr-field-autocomplete__item,
.fr-field-autocomplete__item[tabindex] {
  color: var(--fr-color__grey-200-850);
  cursor: pointer;
  text-decoration: none;
}
a.fr-field-autocomplete__item:focus-visible,
a.fr-field-autocomplete__item:hover,
.fr-field-autocomplete__item[tabindex]:focus-visible,
.fr-field-autocomplete__item[tabindex]:hover {
  background-color: var(--fr-color__grey-1000-50--hover);
}
.fr-field-autocomplete__item[disabled] {
  color: var(--fr-color__grey-425-625);
  cursor: not-allowed;
}
a.fr-field-autocomplete__item--active,
.fr-field-autocomplete__item--active[tabindex] {
  background-color: var(--fr-color__blue-france-sun-113-625);
  color: var(--fr-color__blue-france-975-sun-113);
}
a.fr-field-autocomplete__item--active:focus-visible,
a.fr-field-autocomplete__item--active:hover,
.fr-field-autocomplete__item--active[tabindex]:focus-visible,
.fr-field-autocomplete__item--active[tabindex]:hover {
  background-color: var(--fr-color__blue-france-sun-113-625--hover);
}
</style>
