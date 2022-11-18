<template>
  <v-row>
    <v-col cols="12">
      <v-text-field v-model="userData.email" hide-details filled label="Email" />
    </v-col>
    <v-col cols="12">
      <InputsPasswordTextField v-model="userData.password" />
    </v-col>
    <v-col cols="6">
      <v-text-field v-model="userData.firstname" hide-details filled label="Prénom" />
    </v-col>
    <v-col cols="6">
      <v-text-field v-model="userData.lastname" hide-details filled label="Nom" />
    </v-col>
    <template v-if="userData.email.includes('gouv.fr')">
      <!-- <template> -->
      <v-col cols="">
        <VDeptAutocomplete v-model="userData.dept" />
      </v-col>
      <v-col cols="auto">
        <v-checkbox v-model="userData.isDDT" label="Agent de DDT/DEAL" />
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
        isDDT: false
      }
    }
  }
}
</script>
