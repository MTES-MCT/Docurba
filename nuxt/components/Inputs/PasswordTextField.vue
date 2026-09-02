<template>
  <validation-provider v-slot="{ errors }" name="Mot de passe" :rules="rules">
    <v-text-field
      v-model="password"
      filled
      :error-messages="errors"
      :type="showPassword ? 'text' : 'password'"
      :append-icon="showPassword ? icons.mdiEye : icons.mdiEyeOff"
      v-bind="inputProps"
      @click:append="showPassword = !showPassword"
    />
  </validation-provider>
</template>

<script>
import { mdiEye, mdiEyeOff } from '@mdi/js'
import { ValidationProvider } from 'vee-validate'
export default {
  components: {
    ValidationProvider
  },
  props: {
    value: {
      type: String,
      default: ''
    },
    inputProps: {
      type: Object,
      default () {
        return {
          label: 'Mot de passe'
        }
      }
    },
    optional: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      icons: { mdiEye, mdiEyeOff },
      showPassword: false,
      password: ''
    }
  },
  computed: {
    rules () {
      return `${this.optional ? '' : 'required|'}min:6`
    }
  },
  watch: {
    password () {
      this.$emit('input', this.password)
    }
  }
}
</script>
