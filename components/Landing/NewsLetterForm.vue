<template>
  <v-container>
    <v-row justify="center" align="center">
      <v-col cols="12">
        <h3 class="text-h3">
          Suivre les actualités de la plateforme Docurba
        </h3>
        <p>
          Inscrivez-vous à la newsletter et recevez environ 1 email par mois.
        </p>
      </v-col>
      <v-col cols="6">
        <v-text-field
          v-model="email"
          hide-details
          filled
          label="S'inscrire à la news letter"
          :append-icon="displayedIcon"
          :loading="loading"
          @click:append="sendEmail"
        />
      </v-col>
      <!-- <v-col cols="auto">
        <v-btn depressed tile>S'inscrire à la news letter</v-btn>
      </v-col> -->
    </v-row>
  </v-container>
</template>

<script>
import { mdiArrowRightBold, mdiCheck } from '@mdi/js'

export default {
  data () {
    return {
      displayedIcon: mdiArrowRightBold,
      loading: false,
      email: ''
    }
  },
  methods: {
    async sendEmail () {
      this.loading = true

      await this.$supabase.from('news_letter_emails').insert([{
        email: this.email
      }], { returning: 'minimal' })

      this.loading = false
      this.displayedIcon = mdiCheck
    }
  }
}
</script>
