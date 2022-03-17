<template>
  <v-row>
    <v-col cols="12">
      <v-text-field v-model="userData.email" hide-details filled label="Email" />
    </v-col>
    <v-col cols="12">
      <v-text-field
        v-model="userData.password"
        hide-details
        filled
        label="Mot de passe"
        :type="showPassword ? 'text' : 'password'"
        :append-icon="showPassword ? icons.mdiEye : icons.mdiEyeOff"
        @click:append="showPassword = !showPassword"
      />
    </v-col>
    <v-col cols="12">
      <v-text-field v-model="userData.firstname" hide-details filled label="Prénom" />
    </v-col>
    <v-col cols="12">
      <v-text-field v-model="userData.lastname" hide-details filled label="Nom" />
    </v-col>
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
      showPassword: false,
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
