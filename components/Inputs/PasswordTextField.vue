<template>
  <v-text-field
    v-model="password"
    filled
    :type="showPassword ? 'text' : 'password'"
    :append-icon="showPassword ? icons.mdiEye : icons.mdiEyeOff"
    v-bind="inputProps"
    :error-messages="errorMessages"
    @click:append="showPassword = !showPassword"
    @blur="$emit('blur')"
  />
</template>

<script>
import { mdiEye, mdiEyeOff } from '@mdi/js'

export default {
  props: {
    value: {
      type: String,
      default: ''
    },
    errorMessages: {
      type: Array,
      default: () => []
    },
    inputProps: {
      type: Object,
      default () {
        return {
          label: 'Mot de passe'
        }
      }
    }
  },
  data () {
    return {
      icons: { mdiEye, mdiEyeOff },
      showPassword: false,
      password: ''
    }
  },
  watch: {
    password () {
      this.$emit('input', this.password)
    }
  }
}
</script>
