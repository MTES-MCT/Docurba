<template>
  <v-dialog v-model="dialog" width="400" persistent>
    <v-card>
      <v-card-title>
        Changement de mot de passe
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col>
            <InputsPasswordTextField v-model="password" :input-props="{label: 'Nouveau mot de passe'}" />
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn :loading="loading" color="primary" @click="resetPassword">
          Valider
        </v-btn>
        <v-btn text @click="dialog = false">
          Annuler
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  data () {
    return {
      password: '',
      resetToken: '',
      loading: false,
      dialog: false
    }
  },
  mounted () {
    this.$supabase.auth.onAuthStateChange((event) => {
      if (event === 'PASSWORD_RECOVERY') {
        const params = new URLSearchParams(this.$route.hash.split('#')[1])

        this.resetToken = params.get('access_token')
        this.dialog = true
      } else {
        // console.log('other event', event)
      }
    })
  },
  methods: {
    async resetPassword () {
      this.loading = true

      await this.$supabase.auth.api
        .updateUser(this.resetToken, { password: this.password })

      this.loading = false
      this.dialog = false
    }
  }
}
</script>
