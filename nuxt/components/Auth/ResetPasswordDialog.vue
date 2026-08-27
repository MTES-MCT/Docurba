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
        <v-btn depressed tile :loading="loading" color="primary" @click="resetPassword">
          Valider
        </v-btn>
        <v-btn depressed tile text @click="dialog = false">
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

      await this.$supabase.auth
        .updateUser({ password: this.password })

      this.loading = false
      this.dialog = false
    }
  }
}
</script>
