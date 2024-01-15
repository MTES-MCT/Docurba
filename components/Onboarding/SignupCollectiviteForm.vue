<template>
  <v-row>
    <v-col cols="12">
      <validation-provider v-slot="{ errors }" name="Email" rules="required|email">
        <v-text-field v-model="userData.email" :error-messages="errors" filled label="Email" :disabled="updateCensored" />
      </validation-provider>
    </v-col>
    <v-col cols="12">
      <div class="text-h2">
        Qui êtes vous ?
      </div>
    </v-col>
    <v-col cols="6">
      <validation-provider v-slot="{ errors }" name="Prénom" rules="required">
        <v-text-field v-model="userData.firstname" :error-messages="errors" filled label="Prénom" />
      </validation-provider>
    </v-col>
    <v-col cols="6">
      <validation-provider v-slot="{ errors }" name="Nom" rules="required">
        <v-text-field v-model="userData.lastname" :error-messages="errors" filled label="Nom" />
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
    <v-col>
      <validation-provider v-if="userData.poste === 'autre'" v-slot="{ errors }" name="Intitulé" rules="required">
        <v-text-field
          v-model="userData.other_poste"
          cols="6"
          :error-messages="errors"
          filled
          label="Intitulé"
        />
      </validation-provider>
    </v-col>
    <v-col cols="6">
      <validation-provider v-slot="{ errors }" name="Téléphone professionel" rules="required">
        <v-text-field v-model="userData.tel" :error-messages="errors" filled label="Téléphone professionel" />
      </validation-provider>
    </v-col>
    <v-col cols="12">
      <div class="text-h2">
        <span v-if="userData.poste !== 'be' && userData.poste !== 'agence_urba'">Quelle est votre collectivité ?</span>
        <span v-else>Quelles collectivités accompagnez-vous ?*</span>
      </div>
    </v-col>
    <v-col cols="12">
      <VCollectivitesAutocomplete
        v-model="selectedCollectivite"
        :default-departement-code="userData.departement"
        large
        :cols-dep="4"
        :cols-town="8"
        :input-props="{
          filled: true
        }"
      />
      <span v-if="userData.poste === 'be' || userData.poste === 'agence_urba'">
        *Notez qu’il sera toujours possible d’élargir et modifier votre périmètre par la suite
      </span>
    </v-col>
  </v-row>
</template>

<script>
import FormInput from '@/mixins/FormInput.js'
export default {
  name: 'SignupCollectiviteForm',
  mixins: [FormInput],
  props: {
    value: {
      type: Object,
      default () { return {} }
    },
    updateCensored: {
      type: Boolean,
      default () { return false }
    }
  },
  data () {
    console.log('this.value: ', this.value)
    return {
      selectedCollectivite: { collectivite_id: this.$user.profile.collectivite_id, departement: this.$user.profile.departement },
      postes: [
        { text: 'Bureau d\'étude', value: 'be' },
        { text: 'Elu(e)', value: 'elu' },
        { text: 'Technicien(ne) ou employé(e)', value: 'employe_mairie' },
        { text: 'Agence d\'urbanisme', value: 'agence_urba' },
        { text: 'Autre', value: 'autre' }
      ],
      userData: Object.assign(this.defaultUserData(), this.value)
    }
  },
  computed: {
    selectedCollectiviteId () {
      return this.selectedCollectivite.EPCI || this.selectedCollectivite.code_commune_INSEE || null
    }
  },
  watch: {
    userData: {
      deep: true,
      handler () {
        this.$emit('input', { ...this.userData, collectivite_id: this.selectedCollectiviteId, departement: this.selectedCollectivite.code_departement })
      }
    },
    selectedCollectivite (val) {
      this.$emit('input', { ...this.userData, collectivite_id: this.selectedCollectiviteId, departement: this.selectedCollectivite.code_departement })
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
