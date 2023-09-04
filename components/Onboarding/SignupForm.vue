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
          :items="roles"
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
          :items="postes"
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
      roles: [
        { text: 'DDT/DEAL', value: 'ddt' },
        { text: 'DREAL', value: 'dreal' }
      ],
      postes: [
        { text: 'Chef d\'unité/de bureau/de service et adjoint', value: 'chef_unite' },
        { text: 'Rédacteur(ice) de PAC ', value: 'redacteur_pac' },
        { text: 'Chargé(e) de l\'accompagnement des collectivités', value: 'suivi_procedures' },
        { text: 'Référent(e) Sudocuh', value: 'referent_sudocuh' }

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
        poste: null,
        other_poste: null,
        departement: null,
        region: null
      }
    }
  }
}
</script>
