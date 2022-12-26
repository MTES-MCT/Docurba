<template>
  <v-container id="prescription" class="mb-16">
    <v-row>
      <v-col>
        <h1 class="text-h1">
          Prescriptions
        </h1>
      </v-col>
    </v-row>
    <template v-if="!noPrescription">
      <v-row>
        <v-col cols="12">
          <div class="text-h6 font-weight-bold">
            Le document de prescription pour {{ town.nom_commune_complet }} :
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="8">
          <p class="">
            Document de prescription_Laon.pdf
          </p>
        </v-col>
        <v-col cols="4">
          <v-btn
            class="pa-0"
            outlined
            color="primary"
          >
            <v-icon>{{ icons.mdiDownload }}</v-icon>
          </v-btn>
          <v-btn
            class="pa-0"
            outlined
            color="primary"
          >
            <v-icon>{{ icons.mdiLink }}</v-icon>
          </v-btn>
          <v-btn
            class="pa-0"
            outlined
            color="primary"
          >
            <v-icon>{{ icons.mdiEye }}</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </template>
    <template v-else>
      <v-alert outlined color="primary lighten-2" tile class="pa-0 mb-8 mt-12">
        <div class="d-flex align-center">
          <div class="primary lighten-2 pa-2">
            <v-icon color="white">
              {{ icons.mdiEye }}
            </v-icon>
          </div>
          <div class="ml-4 black--text">
            Il n’y a pas encore de prescription pour cette commune
          </div>
        </div>
      </v-alert>
    </template>
    <v-row>
      <v-col cols="12">
        <v-divider class="my-8" />
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <div class="text-h6 font-weight-bold">
          Vous pouvez mettre à jour la prescription
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <div class="">
          Si vous disposez de la prescription mise à jour, vous pouvez la déposer ici.
        </div>
      </v-col>
      <v-col cols="12">
        <v-btn outlined color="primary" :to="{name: 'prescriptions-add'}">
          Déposer
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mdiDownload, mdiEye, mdiLink } from '@mdi/js'
import axios from 'axios'

export default {
  name: 'Prescriptions',
  data () {
    return {
      noPrescription: false,
      town: null,
      epci: null,
      icons: {
        mdiDownload,
        mdiEye,
        mdiLink
      }
    }
  },
  async mounted () {
    this.loading = true
    if (!this.$route.query.isEpci) {
      this.town = (await axios({
        url: `/api/communes/${this.$route.query.code}`,
        method: 'get'
      })).data
    }

    this.loading = false
  },
  methods: {
  }
}

</script>
