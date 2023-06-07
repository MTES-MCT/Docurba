<template>
  <v-dialog v-model="isOpen" max-width="800px">
    <template #activator="{on}">
      <v-btn color="primary" depressed v-on="on">
        {{ label }}
      </v-btn>
    </template>
    <v-card>
      <v-btn text absolute top right @click="isOpen = false">
        Fermer
        <v-icon class="ml-2" small>
          {{ icons.mdiClose }}
        </v-icon>
      </v-btn>
      <v-card-title>
        Demander l’accès
      </v-card-title>
      <v-card-text>
        <v-form ref="loginForm" v-model="userValid">
          <v-row>
            <v-col cols="12">
              Ces informations seront vérifiées par un administrateur.
            </v-col>
            <v-col cols="12">
              <b>Veuillez indiquer ci-dessous :</b>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="user.lastname" :rules="[$rules.required]" hide-details filled label="Votre nom*" />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="user.firstname" :rules="[$rules.required]" hide-details filled label="Votre prénom*" />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="user.email" :rules="[$rules.required, $rules.email]" hide-details filled label="Votre courriel professionnel*" />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="user.phone" hide-details filled label="Votre numéro de téléphone professionnel" />
            </v-col>
            <v-col cols="6">
              <InputsPasswordTextField
                v-model="user.password"
                :input-props="{
                  label:'Votre mot de passe (min 8 caractères)*',
                  rules: [$rules.required, minLength]
                }"
              />
            </v-col>
            <v-col cols="6">
              <InputsPasswordTextField
                v-model="user.confirmPassword"
                :input-props="{
                  label:'Confirmer votre mot de passe*',
                  rules: [confirmPassword, $rules.required]
                }"
              />
            </v-col>
            <v-col cols="6">
              <v-select label="Votre rôle au sein de votre institution*" :rules="[$rules.required]" filled :items="roles" />
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" outlined depressed @click="isOpen = false">
          Annuler
        </v-btn>
        <v-btn color="primary" depressed :loading="loadingSignup" @click="signupUser">
          Confirmer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script>
import { mdiClose } from '@mdi/js'

export default {
  props: {
    label: { type: String, default: 'Demander l’accès' }
  },
  data () {
    return {
      icons: { mdiClose },
      isOpen: false,
      user: this.getDefaultUserData(),
      loadingSignup: false,
      userValid: false,
      roles: ['Elu', 'Technicien', "Bureau d'étude"]
    }
  },
  methods: {
    getDefaultUserData () {
      return {
        firstname: '',
        lastname: '',
        email: this.$isDev ? `test_${this.$dayjs().format('DD-MM-YY+hhmm')}@docurba.beta.gouv.fr` : '',
        phone: '',
        password: '',
        confirmPassword: '',
        role: ''
      }
    },
    minLength () {
      return this.user.password.length > 8
    },
    confirmPassword () {
      return this.user.password === this.user.confirmPassword
    },
    async signupUser () {
      this.loadingSignup = true

      if (!this.userValid) {
        this.$refs.loginForm.validate()
      } else {
        const { error } = await this.$auth.signUp(this.user)

        if (!error) {
          this.isOpen = false
          this.user = this.getDefaultUserData()
        }
      }

      this.loadingSignup = false
    }
  }
}
</script>
