<template>
  <v-dialog v-model="dialog" width="400" persistent>
    <v-card>
      <validation-observer ref="observerResetPassword" v-slot="{ handleSubmit }">
        <form @submit.prevent="handleSubmit(resetPassword)">
          <v-card-title>
            Changement de mot de passe
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <InputsPasswordTextField v-model="password" :input-props="{label: 'Nouveau mot de passe'}" />
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn depressed tile :loading="loading" color="primary" type="submit">
              Valider
            </v-btn>
            <v-btn depressed tile text @click="signOut()">
              Annuler
            </v-btn>
          </v-card-actions>
        </form>
      </validation-observer>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios'
import FormInput from '@/mixins/FormInput.js'

export default {
  mixins: [FormInput],
  data () {
    return {
      password: '',
      resetToken: '',
      loading: false,
      dialog: false
    }
  },
  computed: {
    isRecoveryRoute () {
      return this.$route.query.type === 'recovery'
    }
  },
  watch: {
    isRecoveryRoute: {
      handler (value) {
        this.dialog = value
      },
      immediate: true
    }
  },
  methods: {
    async resetPassword () {
      this.loading = true

      await this.$djangoApi.post('/api-internes/users/password', {
        password: this.password
      })
      await axios({
        method: 'post',
        url: '/api/auth/password/updated',
        data: {
          email: this.$user.profile.email,
          firstname: this.$user.profile.firstname,
          lastname: this.$user.profile.lastname
        }
      })

      this.loading = false
      this.dialog = false
      this.$router.push({
        name: this.$route.name,
        params: this.$route.params
      })
    },
    async signOut () {
      const { error } = await this.$supabase.auth.signOut()

      if (error) {
        return
      }

      this.$router.push('/')
    }
  }
}
</script>
