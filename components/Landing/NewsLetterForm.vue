<template>
  <v-row>
    <v-col cols="9">
      <v-text-field
        v-model="email"
        hide-details
        filled
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
        height="41px"
        tile
        @click="sendEmail"
      >
        S'abonner
      </v-btn>
    </v-col>
    <v-col cols="12">
      <p class="text-caption mt-2">
        En renseignant votre adresse électronique, vous acceptez de recevoir nos actualités par courriel. Vous pouvez vous désinscrire à tout moment à l’aide des liens de désinscription ou en nous contactant.
      </p>
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
