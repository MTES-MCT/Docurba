<template>
  <v-row>
    <v-col cols="12">
      <v-text-field v-model="userData.email" hide-details filled label="Email" />
    </v-col>
    <v-col cols="12">
      <!-- <v-text-field
        v-model="userData.password"
        hide-details
        filled
        label="Mot de passe"
        :type="showPassword ? 'text' : 'password'"
        :append-icon="showPassword ? icons.mdiEye : icons.mdiEyeOff"
        @click:append="showPassword = !showPassword"
      /> -->
      <InputsPasswordTextField v-model="userData.password" />
    </v-col>
    <v-col cols="6">
      <v-text-field v-model="userData.firstname" hide-details filled label="Prénom" />
    </v-col>
    <v-col cols="6">
      <v-text-field v-model="userData.lastname" hide-details filled label="Nom" />
    </v-col>
    <template v-if="userData.email.includes('gouv.fr')">
      <v-col cols="">
        <VDeptAutocomplete v-model="ddtData.dept" />
      </v-col>
      <v-col cols="auto">
        <v-checkbox v-model="isDDT" label="Agent de DDT" />
      </v-col>
    </template>
  </v-row>
</template>

<script>
import {
  mdiEye,
  mdiEyeOff
} from '@mdi/js'

export default {
  props: {
    value: {
      type: Object,
      default () { return {} }
    }
  },
  data () {
    return {
      icons: {
        mdiEye,
        mdiEyeOff
      },
      ddtData: {
        dept: null
      },
      isDDT: false,
      userData: Object.assign(this.defaultUserData(), this.value)
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
        email: '',
        firstname: '',
        lastname: '',
        password: ''
      }
    }
  }
}
</script>
