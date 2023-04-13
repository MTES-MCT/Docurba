<template>
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
        <DashboardCollectivitesInnerNav :is-epci="isEpci" :collectivite="collectivite" :communes="communes" :region="region" />
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
          <p>Nos équipes vont vérifier votre identité avant de publier la prescription</p>
          <v-text-field v-model="email" type="email" label="Email" filled />
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-btn depressed color="primary" :disabled="!email" @click="nextPage">
          Valider
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
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
    },
    region: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiArrowLeft
      },
      email: ''
    }
  },
  methods: {
    nextPage () {
      this.$emit('snackMessage', 'Vous pouvez dès a présent soumettre votre acte. Nous vous préviendrons par email quand ce dernier sera avalisée.')
      this.$router.push({ name: 'collectivites-collectiviteId-prescriptions-add', params: { collectiviteId: this.isEpci ? this.collectivite.EPCI : this.collectivite.code_commune_INSEE }, query: this.$route.query })
    }
  }

}
</script>

<style lang="scss">
.light-border{
  border: solid 1px var(--v-g300-base);
}

</style>
