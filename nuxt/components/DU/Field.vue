<script>
export default {
  props: {
    disabled: {
      default: false,
      type: Boolean
    },
    error: {
      default: false,
      type: Boolean
    },
    icon: {
      default: undefined,
      type: String
    },
    id: {
      default: undefined,
      type: String
    },
    placeholder: {
      default: undefined,
      type: String
    },
    sm: {
      default: false,
      type: Boolean
    },
    success: {
      default: false,
      type: Boolean
    },
    type: {
      default: 'text',
      type: String
    },
    value: {
      default: '',
      type: [String, Boolean]
    }
  },
  computed: {
    model: {
      get () {
        return this.value
      },
      set (value) {
        this.$emit('input', value)
      }
    }
  }
}
</script>

<template>
  <div
    class="du-field"
    :class="{
      [`du-field--${type}`]: type !== 'text',
      'du-field--error': error,
      'du-field--icon': !!icon,
      'du-field--sm': sm,
      'du-field--success': success,
    }"
  >
    <input
      v-if="type === 'checkbox'"
      :id="id"
      v-model="model"
      class="du-field__input"
      :disabled="disabled ? true : undefined"
      type="checkbox"
    >
    <label
      v-if="$slots.default"
      class="du-field__label"
      :for="id"
    >
      <slot />
      <span
        v-if="$slots.hint"
        class="du-field__hint"
      >
        <slot name="hint" />
      </span>
    </label>
    <div
      v-if="type !== 'checkbox'"
      class="du-field__body"
    >
      <slot name="input">
        <input
          :id="id"
          v-model="model"
          class="du-field__input"
          :disabled="disabled ? true : undefined"
          :placeholder="placeholder"
          :type="type"
        >
      </slot>
      <FRIcon
        v-if="icon"
        :value="icon"
      />
    </div>
    <slot name="description" />
  </div>
</template>

<style>
.du-field {
  display: grid;
  justify-items: start;
  position: relative;
  row-gap: 1rem;
}
.du-field::before {
  background-color: var(--du-field__color, transparent);
  bottom: 0;
  content: '';
  left: -.75rem;
  pointer-events: none;
  position: absolute;
  top: 0;
  width: .125rem;
}
.du-field--checkbox {
  padding-bottom: .5rem;
  padding-top: .5rem;
}
.du-field--checkbox > .du-field__input,
.du-field--checkbox > .du-field__label::before,
.du-field--checkbox > .du-field__label::after {
  height: 1.5rem;
  left: 0;
  position: absolute;
  top: .5rem;
  width: 1.5rem;
}
.du-field--checkbox > .du-field__input {
  opacity: 0;
  padding: 0;
}
.du-field--checkbox > .du-field__input:checked ~ .du-field__label::before {
  box-shadow: inset 0 0 0 .25rem #000091;
}
.du-field--checkbox > .du-field__input:checked ~ .du-field__label::after {
  background-color: #000091;
  mask-composite: exclude;
  mask-image: url('data:image/svg+xml;charset=utf-8,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"%3E%3Cpath fill="%23000000" d="m10 15.17 9.2-9.2 1.4 1.42L10 18l-6.36-6.36 1.4-1.42z"/%3E%3C/svg%3E'),
              linear-gradient(#fff 0 0);
  mask-position: center;
  mask-size: 1rem;
}
.du-field--checkbox > .du-field__input[disabled] ~ .du-field__label {
  cursor: not-allowed;
}
.du-field--checkbox > .du-field__input[disabled] ~ .du-field__label::after {
  box-shadow: inset 0 0 0 .0625rem #e5e5e5;
}
.du-field--checkbox > .du-field__input[disabled]:checked ~ .du-field__label::before {
  background-color: #929292;
  box-shadow: inset 0 0 0 .25rem #e5e5e5;
}
.du-field--checkbox > .du-field__input[disabled]:checked ~ .du-field__label::after {
  background-color: #e5e5e5;
  box-shadow: inset 0 0 0 .0625rem #e5e5e5;
}
.du-field--checkbox > .du-field__label {
  margin-left: 2rem;
}
.du-field--checkbox > .du-field__label::before,
.du-field--checkbox > .du-field__label::after {
  content: '';
  border-radius: .25rem;
}
.du-field--checkbox > .du-field__label::after {
  box-shadow: inset 0 0 0 .0625rem #000091;
}
.du-field--checkbox.du-field--sm {
  padding-bottom: 0;
  padding-top: 0;
}
.du-field--checkbox.du-field--sm > .du-field__input,
.du-field--checkbox.du-field--sm > .du-field__label::before,
.du-field--checkbox.du-field--sm > .du-field__label::after {
  height: 1rem;
  top: .25rem;
  width: 1rem;
}
.du-field--checkbox.du-field--sm > .du-field__label {
  margin-left: 1.5rem;
}
.du-field--error {
  --du-field__color: #ce0500;
}
.du-field--icon > .du-field__body > .du-field__input {
  padding-right: 2.5rem;
}
.du-field--success {
  --du-field__color:  #18753c;
}
.du-field__body {
  display: grid;
  position: relative;
  width: 100%;
}
.du-field__body > .v-icon {
  color: #3a3a3a;
  pointer-events: none;
  position: absolute;
  right: .5rem;
  top: .5rem;
}
.du-field__hint {
  color: #666666;
  font-size:.75rem;
  line-height: 1.25rem;
}
.du-field__input {
  background-color: #eeeeee;
  border-top-left-radius: .25rem;
  border-top-right-radius: .25rem;
  box-shadow: inset 0 -.125rem 0 0 var(--du-field__color, #3a3a3a);
  color: #3a3a3a;
  padding: .5rem 1rem;
  width: 100%;
}
.du-field__label {
  color: var(--du-field__color, #161616);
  cursor: pointer;
  display: grid;
  font-size: 1rem;
  font-weight: 400;
  justify-items: start;
  line-height: 1.5rem;
}
.du-field__label:first-child {
  margin-bottom: -.5rem;
}
</style>
