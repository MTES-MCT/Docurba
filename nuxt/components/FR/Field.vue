<script>
export default {
  props: {
    error: {
      default: false,
      type: Boolean,
    },
    icon: {
      default: undefined,
      type: String,
    },
    id: {
      default: undefined,
      type: String,
    },
    placeholder: {
      default: undefined,
      type: String,
    },
    sm: {
      default: false,
      type: Boolean,
    },
    success: {
      default: false,
      type: Boolean,
    },
    type: {
      default: 'text',
      type: String,
    },
    value: {
      default: '',
      type: [String, Boolean],
    },
  },
  computed: {
    model: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit('input', value)
      },
    },
  },
}
</script>

<template>
  <div class="fr-field"
       :class="{
         [`fr-field--${type}`]: type !== 'text',
         'fr-field--error': error,
         'fr-field--icon': !!icon,
         'fr-field--sm': sm,
         'fr-field--success': success,
       }">
    <input v-if="type === 'checkbox'"
           class="fr-field__input"
           :id="id"
           type="checkbox"
           v-model="model" />
    <FRText v-if="$slots.default"
            class="fr-field__label"
            :for="id"
            tag="label">
      <slot />
      <FRText v-if="$slots.hint"
              mention
              xs>
        <slot name="hint" />
      </FRText>
    </FRText>
    <div v-if="type !== 'checkbox'"
         class="fr-field__body">
      <slot name="input">
        <input class="fr-field__input"
               :id="id"
               :placeholder="placeholder"
               :type="type"
               v-model="model" />
      </slot>
      <FRIcon v-if="icon"
              :value="icon" />
    </div>
    <slot name="description" />
  </div>
</template>

<style>
.fr-field {
  display: grid;
  justify-items: start;
  position: relative;
  row-gap: 1rem;
}
.fr-field::before {
  bottom: 0;
  content: '';
  left: -.75rem;
  pointer-events: none;
  position: absolute;
  top: 0;
  width: .125rem;
}
.fr-field--checkbox {
  padding-bottom: .5rem;
  padding-top: .5rem;
}
.fr-field--checkbox > .fr-field__input,
.fr-field--checkbox > .fr-field__label::before {
  height: 1.5rem;
  left: 0;
  position: absolute;
  top: .5rem;
  width: 1.5rem;
}
.fr-field--checkbox > .fr-field__input {
  opacity: 0;
  padding: 0;
}
.fr-field--checkbox > .fr-field__input:checked ~ .fr-field__label::before {
  background-color: var(--fr-color__blue-france-sun-113-625);
  mask-composite: exclude;
  mask-image: url('data:image/svg+xml;charset=utf-8,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"%3E%3Cpath fill="%23000000" d="m10 15.17 9.2-9.2 1.4 1.42L10 18l-6.36-6.36 1.4-1.42z"/%3E%3C/svg%3E'),
              linear-gradient(#fff 0 0);
}
.fr-field--checkbox > .fr-field__label {
  margin-left: 2rem;
}
.fr-field--checkbox > .fr-field__label::before {
  content: '';
  border-radius: .25rem;
  box-shadow: inset 0 0 0 .0625rem var(--fr-color__blue-france-sun-113-625);
}
.fr-field--checkbox.fr-field--sm {
  padding-bottom: 0;
  padding-top: 0;
}
.fr-field--checkbox.fr-field--sm > .fr-field__input,
.fr-field--checkbox.fr-field--sm > .fr-field__label::before {
  height: 1rem;
  top: .25rem;
  width: 1rem;
}
.fr-field--checkbox.fr-field--sm > .fr-field__label {
  margin-left: 1.5rem;
}
.fr-field--error::before {
  background-color: var(--fr-color__error-425-625);
}
.fr-field--error > .fr-field__body > .fr-field__input {
  box-shadow: inset 0 -.125rem 0 0 var(--fr-color__error-425-625);
}
.fr-field--error > .fr-field__label.fr-text {
  color: var(--fr-color__error-425-625);
}
.fr-field--icon > .fr-field__body > .fr-field__input {
  padding-right: 2.5rem;
}
.fr-field--success::before {
  background-color: var(--fr-color__success-425-625);
}
.fr-field--success > .fr-field__body > .fr-field__input {
  box-shadow: inset 0 -.125rem 0 0 var(--fr-color__success-425-625);
}
.fr-field--success > .fr-field__label.fr-text {
  color: var(--fr-color__success-425-625);
}
.fr-field__body {
  display: grid;
  position: relative;
  width: 100%;
}
.fr-field__body > .fr-icon {
  color: var(--fr-color__grey-200-850);
  pointer-events: none;
  position: absolute;
  right: .5rem;
  top: .5rem;
}
.fr-field__input {
  background-color: var(--fr-color__grey-950-100);
  border-top-left-radius: .25rem;
  border-top-right-radius: .25rem;
  box-shadow: inset 0 -.125rem 0 0 var(--fr-color__grey-200-850);
  color: var(--fr-color__grey-200-850);
  padding: .5rem 1rem;
  width: 100%;
}
.fr-field__label {
  color: var(--fr-color__grey-50-1000);
  cursor: pointer;
  display: grid;
  justify-items: start;
  row-gap: .25rem;
}
.fr-field__label.fr-text {
  color: var(--fr-color__grey-50-1000);
}
.fr-field__label:first-child {
  margin-bottom: -.5rem;
}
</style>
