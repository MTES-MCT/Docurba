<template>
  <v-container>
    <v-row justify="center" align="center">
      <v-col cols="12" md="5">
        <h3 class="text-h5">
          <b>Abonnez-vous à notre lettre d’information</b>
        </h3>
        <p class="mt-2">
          Suivez l’avancée de nos travaux au fur et à mesure.Rythme d’environ une par mois.
        </p>
      </v-col>
      <v-col cols="12" md="6" md-offset="1">
        <v-row no-gutters>
          <v-col cols="">
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
      }])

      this.loading = false
      this.displayedIcon = mdiCheck
    }
  }
}
</script>
