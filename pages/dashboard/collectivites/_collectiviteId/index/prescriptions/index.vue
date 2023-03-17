<template>
  <v-container v-if="!loading" id="prescription" class="mb-16">
    <v-row align="end">
      <v-col cols="auto">
        <h2>Prescription</h2>
      </v-col>
      <v-col>
        <DashboardCollectivitesInnerNav />
      </v-col>
    </v-row>
    <template v-if="prescription">
      <v-row>
        <v-col cols="12">
          <div class="text-h6 font-weight-bold">
            Le document de prescription pour {{ isEpci ? $route.query.epci_label : collectivite.nom_commune_complet }} :
          </div>
        </v-col>
      </v-row>
      <v-alert v-if="$route.query.success" outlined color="success lighten-2" tile class="pa-0 mb-8 mt-12">
        <div class="d-flex align-center ">
          <div class="success lighten-2 py-4 px-3 fill-height">
            <v-icon color="white">
              {{ icons.mdiCheckCircle }}
            </v-icon>
          </div>
          <div class="ml-4 black--text pa-4">
            Votre document a bien été ajouté.
          </div>
        </div>
      </v-alert>
      <PrescriptionItemListRead :value="prescription" />
      <v-row>
        <v-col cols="12">
          <v-btn outlined color="primary" @click="showHistory = !showHistory">
            <span><span v-if="!showHistory">Afficher</span><span v-else>Cacher</span> l'historique</span>
          </v-btn>
        </v-col>
      </v-row>
      <v-row v-if="showHistory">
        <v-col
          v-for="prescrHistory in history"
          :key="`prescrData-${prescrHistory.id}`"
          cols="12"
        >
          <PrescriptionItemListRead :value="prescrHistory" />
        </v-col>
      </v-row>
    </template>
    <template v-else>
      <v-alert outlined color="primary lighten-2" tile class="pa-0 mb-8 mt-12">
        <div class="d-flex align-center ">
          <div class="primary lighten-2 py-4 px-3 fill-height">
            <v-icon color="white">
              {{ icons.mdiInformation }}
            </v-icon>
          </div>
          <div class="ml-4 black--text pa-4">
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
        <v-btn outlined color="primary" :to="{name: 'prescriptions-add', query: {...$route.query, success:false}}">
          Déposer
        </v-btn>
      </v-col>
    </v-row>
    <v-snackbar v-model="snackClip" color="primary">
      L'addresse est copiée dans le presse papier
      <template #action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="snackClip = false"
        >
          Fermer
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
  <VGlobalLoader v-else />
</template>

<script>
import { mdiDownload, mdiEye, mdiLink, mdiInformation, mdiCheckCircle } from '@mdi/js'
// import axios from 'axios'

export default {
  name: 'Prescriptions',
  props: {
    isEpci: {
      type: Boolean,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      noPrescription: false,
      // collectivite: null,
      epci: null,
      loading: true,
      prescription: null,
      snackClip: false,
      history: null,
      showHistory: false,
      icons: {
        mdiDownload,
        mdiInformation,
        mdiEye,
        mdiLink,
        mdiCheckCircle
      }
    }
  },
  async mounted () {
    this.loading = true
    //    this.$route.query.insee

    // const inseeSearch = Array.isArray(this.$route.query.insee) ? this.$route.query.insee : [this.$route.query.insee]
    const inseeSearch = this.isEpci ? [this.collectivite.code_commune_INSEE] : [this.collectivite.code_commune_INSEE]
    console.log('inseeSearch: ', inseeSearch)
    const { data: prescriptions } = await this.$supabase.from('prescriptions').select('*').contains('towns', inseeSearch).order('created_at', { ascending: false })
    console.log('prescriptions: ', prescriptions)
    const [current, ...history] = prescriptions
    this.prescription = current // prescriptions[0]
    this.history = history
    this.loading = false
  }
}

</script>
