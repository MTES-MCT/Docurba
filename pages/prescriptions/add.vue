<template>
  <v-container id="prescription">
    <v-row>
      <v-col>
        <h1 class="text-h1">
          Prescriptions
        </h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-container v-if="!choiceDone" class=" primary lighten-1 pa-8 pb-0">
          <v-row>
            <v-col cols="12">
              <div class="text-h5 font-weight-bold primary--text pb-8">
                Déposer une prescription
              </div>
              <div class="text-h6 font-weight-bold">
                Pour ?
              </div>
            </v-col>
            <v-col cols="12" md="8" class="pt-0">
              <v-radio-group v-model="type" row class="mt-0">
                <v-radio
                  label="Commune"
                  value="commune"
                />
                <v-radio
                  label="EPCI"
                  value="EPCI"
                />
              </v-radio-group>
              <VTownAutocomplete v-if="type === 'commune'" v-model="town" />
              <VEpciAutocomplete v-else v-model="epci" />
            </v-col>
            <v-col cols="12" class="d-flex justify-center py-8">
              <v-btn color="primary" depressed @click="choiceDone = true">
                Valider
              </v-btn>
            </v-col>
          </v-row>
        </v-container>
        <v-container v-else class=" primary lighten-1 pa-8 ">
          <v-row>
            <v-col cols="12">
              <div class="text-h5 font-weight-bold primary--text pb-8 d-flex justify-space-between align-center">
                <div>Vous voulez...</div>
                <div>
                  <v-btn color="primary" text @click="choiceDone = false">
                    <v-icon class="mr-1">
                      {{ icons.mdiPencil }}
                    </v-icon>
                    Modifier
                  </v-btn>
                </div>
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
    <v-row class="pb-16">
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
  </v-container>
</template>

<script>
import { mdiUpload, mdiPencil, mdiCheck } from '@mdi/js'

export default {
  name: 'Prescriptions',
  data () {
    return {
      town: null,
      epci: null,
      choiceDone: false,
      type: 'commune',
      icons: {
        mdiUpload,
        mdiPencil,
        mdiCheck
      }
    }
  },
  watch: {
    type (newVal) {
      console.log('type: ', this.type)
      if (newVal === 'commune') {
        this.epci = null
      } else {
        this.town = null
      }
    }
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
