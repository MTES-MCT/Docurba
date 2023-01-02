<template>
  <v-container v-if="!loading" id="prescription" class="mb-16">
    <v-row>
      <v-col>
        <h1 class="text-h1">
          Prescriptions
        </h1>
      </v-col>
    </v-row>
    <template v-if="prescription">
      <v-row>
        <v-col cols="12">
          <div class="text-h6 font-weight-bold">
            Le document de prescription pour {{ isEpci ? $route.query.epci_label : town.nom_commune_complet }} :
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
      <div v-if="prescription && prescription.type === 'link'">
        <v-row
          align="center"
        >
          <v-col cols="8">
            <div>
              Lien vers le <a target="__blank" :href="prescription.link_url">Document de prescription</a>
            </div>
          </v-col>
          <v-col cols="4">
            <v-btn
              class="pa-0"
              outlined
              color="primary"
              @click="copyLinktoClip"
            >
              <v-icon>{{ icons.mdiLink }}</v-icon>
            </v-btn>
            <v-btn
              class="pa-0"
              outlined
              color="primary"
              target="__blank"
              :href="prescription.link_url"
            >
              <v-icon>{{ icons.mdiEye }}</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </div>

      <div v-if="prescription && prescription.type === 'attachments'">
        <v-row
          v-for="prescrData in prescription.attachments"
          :key="`prescrData-${prescrData.id}`"
          align="center"
        >
          <v-col cols="8">
            <div>
              Fichier <a target="__blank" href="" @click="downloadFile(prescrData)">{{ prescrData.name }}</a>
            </div>
            <a :ref="`file-${prescrData.id}`" :download="prescrData.name" class="d-none" />
          </v-col>
          <v-col cols="4">
            <v-btn
              class="pa-0"
              outlined
              color="primary"
              @click="downloadFile(prescrData)"
            >
              <v-icon>{{ icons.mdiDownload }}</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </div>
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
import axios from 'axios'

export default {
  name: 'Prescriptions',
  data () {
    return {
      noPrescription: false,
      town: null,
      epci: null,
      loading: true,
      prescription: null,
      snackClip: false,
      icons: {
        mdiDownload,
        mdiInformation,
        mdiEye,
        mdiLink,
        mdiCheckCircle
      }
    }
  },
  computed: {
    isEpci () {
      return this.$route.query.insee.epci_label && this.$route.query.insee.epci_code
    }
  },
  async mounted () {
    this.loading = true

    if (!this.isEpci) {
      this.town = (await axios({
        url: `/api/communes/${this.$route.query.insee}`,
        method: 'get'
      })).data
    }
    const { data: prescription } = await this.$supabase.from('prescriptions').select('*').contains('towns', ['1001']).order('created_at', { ascending: false }).limit(1)

    this.prescription = prescription[0]
    console.log('prescription: ', this.prescription)
    this.loading = false
  },
  methods: {
    async downloadFile (file) {
      console.log('file: ', file)
      const { data } = await this.$supabase.storage.from('prescriptions').download(file.path)
      console.log('data: ', data)
      const link = this.$refs[`file-${file.id}`][0]
      link.href = URL.createObjectURL(data)
      link.click()
    },
    copyLinktoClip () {
      navigator.clipboard.writeText(this.prescription.link_url)
      this.snackClip = true
    }
  }

}

</script>
