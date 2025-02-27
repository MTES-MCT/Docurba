<template>
  <v-row>
    <v-col cols="12">
      <validation-provider v-slot="{ errors }" name="Email" rules="required|email">
        <v-text-field v-model="userData.email" :error-messages="errors" filled label="Email" />
      </validation-provider>
    </v-col>
    <v-col cols="12">
      <InputsPasswordTextField v-model="userData.password" />
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
      <validation-provider v-slot="{ errors }" name="Administration" rules="required">
        <v-select
          v-model="userData.poste"
          :error-messages="errors"
          :items="postes"
          filled
          label="Administration"
        />
      </validation-provider>
    </v-col>
    <v-col v-if="userData.poste === 'ddt'" cols="6">
      <validation-provider v-slot="{ errors }" name="Rôle(s)" rules="required">
        <v-select
          v-model="userData.other_poste"
          multiple
          :error-messages="errors"
          :items="roles"
          filled
          label="Rôle(s)"
        />
      </validation-provider>
    </v-col>
    <v-col v-if="userData.poste === 'ddt'" cols="12">
      <validation-provider v-slot="{ errors }" name="Département" rules="required">
        <VDeptAutocomplete v-model="userData.departement" :error-messages="errors" />
      </validation-provider>
    </v-col>
    <v-col v-if="userData.poste === 'dreal'" cols="12">
      <validation-provider v-slot="{ errors }" name="Région" rules="required">
        <VRegionAutocomplete v-model="userData.region" label="Votre region" :error-messages="errors" />
      </validation-provider>
    </v-col>
    <v-col cols="12">
      <v-checkbox
        v-model="userData.optin"
        label="Cochez cette case afin de recevoir nos lettres d'informations mensuelles pour ne rien louper aux dernières actualités de Docurba.
Promis, seul un contenu court et pertinent vous sera envoyé une fois par mois 🌎"
        color="primary"
        hide-details
      />
    </v-col>
  </v-row>
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
      postes: Object.entries(this.$utils.POSTES_ETAT).map(
        ([value, text]) => ({ value, text })
      ),
      roles: Object.entries(this.$utils.ROLES_ETAT).map(
        ([value, text]) => ({ value, text })
      ),
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
        email: this.$isDev ? `fabien+${this.$dayjs().format('DD-MM-YY-hhmm')}@quantedsquare.com` : '',
        firstname: this.$isDev ? 'Test' : '',
        lastname: this.$isDev ? 'Test' : '',
        password: this.$isDev ? 'docurba12345' : '',
        poste: null,
        other_poste: null,
        departement: null,
        region: null,
        optin: false
      }
    }
  }
}
</script>
