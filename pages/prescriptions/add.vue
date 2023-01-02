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
        <v-container class=" primary lighten-1 pa-8 mb-6">
          <v-row>
            <v-col cols="12">
              <div class="text-h5 font-weight-bold primary--text pb-8 d-flex  align-center">
                <v-icon color="primary" large class="mr-2">
                  {{ icons.mdiAccountSearchOutline }}
                </v-icon>

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
                  Pour {{ $route.query.epci_code ? $route.query.epci_label : town.nom_commune_complet }}
                </div>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <div class="text-h6 font-weight-bold">
          Comment souhaitez-vous déposer votre fichier ?
        </div>
      </v-col>
      <v-col cols="12">
        <v-radio-group
          v-model="docType"
          class="mt-0"
          hide-details
          row
        >
          <v-radio
            class="radio-border black--text pa-6 "
            label="Téléverser un fichier"
            value="attachments"
          />
          <v-radio
            class="radio-border black--text pa-6 "
            label="Insérer un lien"
            value="link"
          />
        </v-radio-group>
      </v-col>
      <v-col v-if="docType" cols="12">
        <div class=" black--text">
          Déposez ici votre document de prescription
        </div>
      </v-col>
    </v-row>
    <v-row v-if="docType === 'attachments'">
      <v-col cols="12">
        <div class="mb-8">
          <v-row
            v-for="(file, i) in files"
            :key="`${file.name}--${i}`"
            align="center"
          >
            <v-col cols="8" class="py-1">
              <div>
                {{ file.name }}
              </div>
            </v-col>
            <v-col cols="4" class="py-1">
              <v-btn
                class="pa-0"
                outlined
                color="primary"
                small
                @click="removeFile(file)"
              >
                <v-icon>{{ icons.mdiDelete }}</v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </div>
        <VFileDropzone class="drop-zone" @change="setFiles">
          <div class="dropzone text-center text--secondary rounded pa-8">
            <v-icon class="pb-6" color="primary">
              {{ icons.mdiUpload }}
            </v-icon>

            <div>Glisser le fichier dans cette zone ou cliquez sur le bouton pour ajouter un document</div>
            <div class="py-8">
              <!-- Taille maximale : xx Mo.
              <br> -->
              Formats acceptés : jpg, png, pdf.
            </div>
            <v-btn color="primary" outlined>
              Ajout un document
            </v-btn>
          </div>
        </VFileDropzone>
      </v-col>
    </v-row>
    <v-row v-if="docType === 'link'">
      <v-col cols="12" md="10">
        <v-text-field ref="urlTextfield" v-model="link" filled placeholder="documentprescription.com" :rules="urlRules" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" class="d-flex mb-16">
        <v-btn color="primary" depressed :disabled="!choiceDone" :loading="loadingSave" @click="submitPrescription">
          {{ docType === 'link'? 'Lier le document' : 'Déposer' }}
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
  <VGlobalLoader v-else />
</template>

<script>
import { mdiUpload, mdiPencil, mdiCheck, mdiAccountSearchOutline, mdiDelete } from '@mdi/js'
import axios from 'axios'
import slugify from 'slugify'
import { v4 as uuidv4 } from 'uuid'

export default {
  name: 'PrescriptionsAdd',
  data () {
    return {
      town: null,
      epci: null,
      type: 'commune',
      loading: true,
      loadingSave: false,
      docType: null,
      link: null,
      files: null,
      icons: {
        mdiUpload,
        mdiPencil,
        mdiCheck,
        mdiAccountSearchOutline,
        mdiDelete
      },
      urlRules: [
        v => !!v || 'Une addresse URL est requise.',
        // eslint-disable-next-line
        v => /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi.test(v) || 'L\'addresse URL n\'est pas valide.'
      ]
    }
  },
  computed: {
    choiceDone () {
      return (this.docType === 'attachments' && this.files && this.files.length > 0) || (this.docType === 'link' && this.link && this.$refs?.urlTextfield?.valid)
    }
  },
  async  mounted () {
    this.loading = true
    if (!this.$route.query.epci_code) {
      this.town = (await axios({
        url: `/api/communes/${this.$route.query.insee}`,
        method: 'get'
      })).data
    }

    this.loading = false
  },
  methods: {
    removeFile (file) {
      console.log('File to delete: ', file)
      console.log('this.files: ', this.files)
      this.files = [...this.files].filter(e => e !== file)
    },
    setFiles (files) {
      this.files = files
    },

    async uploadFiles () {
      if (this.files.length) {
        const uploadTimestamp = Date.now()
        const filesData = []
        for (let fileIndex = 0; fileIndex < this.files.length; fileIndex++) {
          const file = this.files[fileIndex]

          // <type_epci_commune>/<insee_or_code>/<date>/files
          const path = `${this.$route.query.epci_code ? 'epci' : 'commune'}/${this.$route.query.epci_code ? this.$route.query.epci_code : this.$route.query.insee}/${uploadTimestamp}/${slugify(file.name, '_')}`
          await this.$supabase.storage
            .from('prescriptions')
            .upload(path, file)
          filesData.push({ path, name: file.name, id: uuidv4() })
        }
        return filesData
      } else {
        throw new Error('Pas de fichier à téléverser')
      }
    },

    async submitPrescription () {
      try {
        this.loadingSave = true
        const prescription = {
          epci: null,
          towns: Array.isArray(this.$route.query.insee) ? this.$route.query.insee : [this.$route.query.insee],
          attachments: null,
          type: this.docType

        }
        if (this.docType === 'link') {
          prescription.link_url = this.link
        } else if (this.docType === 'attachments') {
          prescription.attachments = await this.uploadFiles()
        }

        await this.$supabase.from('prescriptions').insert([prescription])
        this.loadingSave = false
        this.$router.push({ name: 'prescriptions', query: { ...this.$route.query, success: true } })
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

#prescription .radio-border{
    border: solid 1px var(--v-primary-base);
    width: 350px;
    label {
      color: black !important;
    }

}
</style>
