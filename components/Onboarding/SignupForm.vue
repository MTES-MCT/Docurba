<template>
  <v-row>
    <v-col cols="12">
      <validation-provider v-slot="{ errors }" name="Email" rules="required|email">
        <v-text-field v-model="userData.email" :error-messages="errors" filled label="Email" />
      </validation-provider>
    </v-col>
    <v-col cols="12">
      <validation-provider v-slot="{ errors }" name="Mot de passe" rules="required|min:6">
        <InputsPasswordTextField v-model="userData.password" :error-messages="errors" />
        test{{ errors }}
        <!-- NE march pas car le V-model n'est pas direct comparé a VBiGRadio -->
      </validation-provider>
    </v-col>
    <v-col cols="6">
      <validation-provider v-slot="{ errors }" name="Prénom" rules="required">
        <v-text-field v-model="userData.firstname" filled label="Prénom" :error-messages="errors" />
      </validation-provider>
    </v-col>
    <v-col cols="6">
      <validation-provider v-slot="{ errors }" name="Nom" rules="required">
        <v-text-field v-model="userData.lastname" filled label="Nom" :error-messages="errors" />
      </validation-provider>
    </v-col>
    <v-col cols="6">
      <validation-provider v-slot="{ errors }" name="Poste" rules="required">
        <v-select
          v-model="userData.poste"
          :error-messages="errors"
          :items="postes"
          filled
          label="Poste"
        />
      </validation-provider>
    </v-col>

    <v-col v-if="userData.poste === 'ddt'" cols="12">
      <VDeptAutocomplete v-model="userData.dept" />
    </v-col>
    <v-col v-if="userData.poste === 'dreal'" cols="12">
      <VRegionAutocomplete v-model="userData.region" label="Votre region" return-iso />
    </v-col>
  </v-row>
  </form>
  </validation-observer>
</template>

<script>
import {
  mdiEye,
  mdiEyeOff
} from '@mdi/js'

import FormInput from '@/mixins/FormInput.js'

export default {
  mixins: [FormInput],
  props: {
    value: {
      type: Object,
      default () { return {} }
    }
  },
  data () {
    return {
      postes: [
        { text: 'DDT', value: 'ddt' },
        { text: 'DREAL', value: 'dreal' }
      ],
      icons: {
        mdiEye,
        mdiEyeOff
      },
      userData: Object.assign(this.defaultUserData(), this.$isDev ? {} : this.value)
    }
  },
  watch: {
    userData: {
      deep: true,
      handler () {
        this.$emit('input', this.userData)
      }
    }
  },
  methods: {
    defaultUserData () {
      return {
        email: this.$isDev ? `test_${this.$dayjs().format('DD-MM-YY+hhmm')}@docurba.beta.gouv.fr` : '',
        firstname: this.$isDev ? 'Test' : '',
        lastname: this.$isDev ? 'Test' : '',
        password: this.$isDev ? 'docurba12345' : '',
        dept: null,
        region: null,
        isDDT: true
      }
    }
  }
}
</script>
