<template>
  <v-row>
    <v-col cols="9">
      <v-text-field
        v-model="email"
        hide-details
        outlined
        dense
        placeholder="Votre adresse électronique (ex. : nom@domaine.fr)"
        :loading="loading"
        @click:append="sendEmail"
      />
    </v-col>
    <v-col cols="auto">
      <v-btn
        color="primary"
        depressed
        outlined
        height="41px"
        @click="sendEmail"
      >
        S'abonner
      </v-btn>
    </v-col>
  </v-row>
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
      }])

      this.loading = false
      this.displayedIcon = mdiCheck
    }
  }
}
</script>
