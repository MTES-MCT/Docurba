<template>
  <validation-provider v-slot="{ errors: validationErrors }" name="Mot de passe" :rules="rules">
    <v-text-field
      v-model="password"
      filled
      :error-messages="[...validationErrors, ...errors]"
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
    creation: {
      type: Boolean,
      default: false
    },
    errors: {
      type: Array,
      default: () => []
    },
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
      const rules = ['required']

      if (this.creation) {
        rules.push('complex', 'min:16')
      }

      return rules.join('|')
    }
  },
  watch: {
    password () {
      this.$emit('input', this.password)
    }
  }
}
</script>
