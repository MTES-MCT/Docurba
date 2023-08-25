<template>
  <v-form
    ref="form"
    v-model="valid"
    lazy-validation
    @submit.prevent="nextPage"
  >
    <v-container id="prescription" class="mb-16">
      <v-row>
        <v-col>
          <div class="d-flex align-center primary--text text-decoration-underline" @click="$router.back()">
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            Revenir vers les actes déposés
          </div>
        </v-col>
      </v-row>
      <v-row align="end">
        <v-col cols="auto">
          <h2>Actes</h2>
        </v-col>
        <v-col>
          <DashboardCollectivitesInnerNav :is-epci="isEpci" :collectivite="collectivite" :communes="communes" />
        </v-col>
      </v-row>
      <PrescriptionYouWantCard />
      <!-- <v-row>
      <v-col cols="12">
        <div class="text-h6 font-weight-bold">
          Comment souhaitez-vous vous identifier ?
        </div>
      </v-col>
    </v-row> -->
      <v-row>
        <v-col cols="12">
          <!-- <div class="light-border pa-6">
          <p class="text-h6">
            Connectez-vous pour déposer votre prescription
          </p>
          <div class="d-flex align-center primary--text text-decoration-underline" @click="$router.back()">
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            Se connecter
          </div>
        </div>
        <div class="my-4">
          Ou
        </div> -->
          <div class="light-border pa-6">
            <p class="text-h6">
              Indiquez votre adresse mail
            </p>
            <p>Nos équipes vont vérifier votre identité avant de publier l'acte</p>
            <v-alert v-if="error" type="error">
              {{ error }}
            </v-alert>
            <v-text-field
              v-model="email"
              :rules="emailRules"
              required
              type="email"
              label="Email"
              filled
            />
          </div>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-btn depressed color="primary" :disabled="!valid" type="submit">
            Valider
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script>
import { mdiArrowLeft } from '@mdi/js'
export default {
  name: 'ActeSignup',
  props: {
    isEpci: {
      type: Boolean,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    },
    communes: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      valid: false,
      icons: {
        mdiArrowLeft
      },
      emailRules: [
        v => !!v || 'L\'e-mail est requis',
        v => /.+@.+\..+/.test(v) || 'L\'e-mail doit être valide'
      ],
      email: '',
      error: ''
    }
  },
  methods: {
    async  nextPage () {
      try {
        const { data: profile, error: errorProfile } = this.$supabase.from('profiles').select().eq('email', this.email)
        if (errorProfile) { throw errorProfile }
        if (profile.length > 0) { throw new Error('Cet e-mail à déjà un compte rattaché, merci de vous connecter.') }
        const { data: newProfile, error: errorNewProfile } = await this.$supabase.from('profiles').insert({ email: this.email, side: 'collectivite', no_signup: true }).select
        if (errorNewProfile) { throw errorNewProfile }
        this.$emit('snackMessage', 'Vous pouvez dès a présent soumettre votre acte. Nous vous préviendrons par email quand ce dernier sera avalisée.')
        this.$router.push({ name: 'collectivites-collectiviteId-prescriptions-add', params: { collectiviteId: this.isEpci ? this.collectivite.EPCI : this.collectivite.code_commune_INSEE }, query: { email: this.email, user_id: newProfile.id, ...this.$route.query } })
      } catch (error) {
        this.error = error.message
      }
    }
  }

}
</script>

<style lang="scss">
.light-border{
  border: solid 1px var(--v-g300-base);
}

</style>
