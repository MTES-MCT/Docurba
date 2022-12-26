<template>
  <v-container v-if="!loading" id="prescription">
    <v-row>
      <v-col>
        <h1 class="text-h1">
          Prescriptions
        </h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-container class=" primary lighten-1 pa-8 ">
          <v-row>
            <v-col cols="12">
              <div class="text-h5 font-weight-bold primary--text pb-8 d-flex  align-center">
                <div>Vous voulez...</div>
              </div>
              <div>
                <div class="mb-4">
                  <v-icon color="primary" class="mr-1">
                    {{ icons.mdiCheck }}
                  </v-icon>
                  Déposer une prescription <span class="text-capitalize">{{ type }}</span>
                </div>
                <div>
                  <v-icon color="primary" class="mr-1">
                    {{ icons.mdiCheck }}
                  </v-icon>
                  Pour
                  <span v-if="type === 'commune'">{{ town.nom_commune }}</span>
                  <span v-else>{{ epci.label }}</span>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
    <v-row v-if="docType === 'upload'" class="pb-16">
      <v-col cols="12">
        <div class="pt-8 black--text">
          Déposez ici votre document de prescription
        </div>
      </v-col>
      <v-col cols="12">
        <VFileDropzone>
          <div class="dropzone text-center text--secondary rounded pa-8">
            <v-icon class="pb-6" color="primary">
              {{ icons.mdiUpload }}
            </v-icon>

            <div>Glisser le fichier dans cette zone ou cliquez sur le bouton pour ajouter un document</div>
            <div class="py-8">
              Taille maximale : xx Mo.
              <br>
              Formats acceptés : jpg, png, pdf.
            </div>
            <v-btn color="primary" outlined>
              Ajout un document
            </v-btn>
          </div>
        </VFileDropzone>
      </v-col>
      <v-col cols="12" class="d-flex justify-end">
        <v-btn color="primary" depressed :disabled="!choiceDone" @click="uploadPrescription">
          Valider
        </v-btn>
      </v-col>
    </v-row>
    <v-row v-else class="pb-16">
      <v-col cols="12">
        <div class="pt-8 black--text">
          LINK
        </div>
      </v-col>
    </v-row>
  </v-container>
  <VGlobalLoader v-else />
</template>

<script>
import { mdiUpload, mdiPencil, mdiCheck } from '@mdi/js'
import axios from 'axios'

export default {
  name: 'PrescriptionsAdd',
  data () {
    return {
      town: null,
      epci: null,
      type: 'commune',
      loading: true,
      docType: 'link',
      icons: {
        mdiUpload,
        mdiPencil,
        mdiCheck
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
    async uploadPrescription () {
      try {
        console.log('uploadPrescription')
        const prescription = {
          epci: {},
          towns: [],
          attachements: []
        }
        await this.$supabase.from('prescriptions').insert([prescription])
      } catch (error) {
        console.log(error)
      }
    }
  }
}
</script>

<style lang="scss" >
#prescription .dropzone{
  cursor: pointer;
  border: dashed 2px var(--v-primary-base);
}
</style>
