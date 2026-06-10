<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Options } from '@/data/Option'
import FrAutocomplete from '@/components/FrAutocomplete.vue'
import FrCheckbox from '@/components/FrCheckbox.vue'
import FrChecklist from '@/components/FrChecklist.vue'
import FrInput from '@/components/FrInput.vue'
import FrSelect from '@/components/FrSelect.vue'
import { useAttrsAndClassName } from '@/composables/useAttrsAndClassName'

interface Props {
  error?: boolean | string
  fieldClass?: string | undefined
  id: string
  options?: Options<string>
  success?: boolean | string
  type?: string
}

const {
  error = false,
  fieldClass,
  id,
  options = [],
  success = false,
  type = 'text',
} = defineProps<Props>()
const selection = defineModel<Array<string>>('selection', { default: [] })
const value = defineModel<string>('value', { default: '' })
defineOptions({
  inheritAttrs: false,
})

const visible = ref(false)

const { attrs, className } = useAttrsAndClassName()

const autocomplete = computed<boolean>(() => type === 'autocomplete')
const checklist = computed<boolean>(() => type === 'checklist')
const inputType = computed<string>(() =>
  password.value
    ? (visible.value ? 'text' : 'password')
    : type
)
const message = computed<string>(() => {
  if (typeof error === 'string') {
    return error
  }
  if (typeof success === 'string') {
    return success
  }

  return ''
})
const password = computed<boolean>(() => type === 'password')
const select = computed<boolean>(() => type === 'select')
</script>

<template>
  <div class="fr-field"
       :class="{
         'fr-field--error': !!error,
         'fr-field--success': !!success,
         [className]: !!className,
       }">
    <label v-if="$slots.label"
           class="fr-field__label"
           :for="id">
      <slot name="label" />
      <span v-if="$slots.hint"
            class="fr-field__hint">
        <slot name="hint" />
      </span>
    </label>
    <component :is="
                 autocomplete
                   ? FrAutocomplete
                   : checklist
                     ? FrChecklist
                     : select
                       ? FrSelect
                       : FrInput
               "
               v-bind="attrs"
               class="fr-field__input"
               :class="fieldClass"
               :error="!!error"
               :id="id"
               :options="autocomplete || checklist || select ? options : undefined"
               :success="!!success"
               :type="password ? inputType : undefined"
               v-model:value="value"
               v-model:selection="selection" />
    <FrCheckbox v-if="password"
                class="fr-field__visibility"
                :id="`${id}-visibility`"
                v-model:value="visible">Afficher</FrCheckbox>
    <p v-if="$slots.message || message"
        class="fr-field__message">
      <slot name="message">{{ message }}</slot>
    </p>
  </div>
</template>

<style>
.fr-field {
  align-items: start;
  display: grid;
  gap: .5rem;
  grid-auto-columns: 1fr auto;
  position: relative;
}
.fr-field--error .fr-field__label,
.fr-field--error .fr-field__message {
  color: var(--color-error-425-625);
}
.fr-field--error .fr-field__label::before,
.fr-field--error .fr-field__message::before,
.fr-field--success .fr-field__label::before,
.fr-field--success .fr-field__message::before {
  content: '';
}
.fr-field--error .fr-field__message::before {
  mask-image: url('@/assets/icons/error-fill.svg');
}
.fr-field--success .fr-field__label,
.fr-field--success .fr-field__message {
  color: var(--color-success-425-625);
}
.fr-field--success .fr-field__message::before {
  mask-image: url('@/assets/icons/success-fill.svg');
}
.fr-field__hint {
  color: var(--color-grey-425-625);
  font-size: .75rem;
  line-height: 1.25rem;
}
.fr-field__input,
.fr-field__message {
  grid-column: 1 / span 2;
}
.fr-field__label,
.fr-field__visibility {
  order: -1;
}
.fr-field__label {
  color: var(--color-grey-50-1000);
  display: grid;
  font-family: var(--font-family-sans);
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5rem;
  row-gap: .25rem;
}
.fr-field__label::before {
  background-color: currentColor;
  display: grid;
  height: 100%;
  left: -.75rem;
  pointer-events: none;
  position: absolute;
  top: 0;
  width: .125rem;
}
.fr-field__message {
  color: var(--color-grey-425-625);
  font-family: var(--font-family-sans);
  font-size: .75rem;
  font-weight: 400;
  line-height: 1.25rem;
  margin-bottom: 0;
  margin-top: .5rem;
}
.fr-field__message::before {
  background-color: currentColor;
  display: inline-block;
  height: 1rem;
  margin-right: .25rem;
  margin-top: .125rem;
  mask-size: 100% 100%;
  pointer-events: none;
  vertical-align: top;
  width: 1rem;
}
.fr-field__visibility {
  grid-column-start: 2;
}
</style>
