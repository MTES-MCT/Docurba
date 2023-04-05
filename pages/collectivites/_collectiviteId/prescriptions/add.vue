<template>
  <v-container id="prescription">
    <v-row align="end">
      <v-col cols="auto">
        <h2>Actes</h2>
      </v-col>
      <v-col>
        <DashboardCollectivitesInnerNav :is-epci="isEpci" :collectivite="collectivite" :communes="communes" :region="region" />
      </v-col>
    </v-row>

    <PrescriptionYouWantCard />
    <v-row>
      <v-col cols="12" class="mb-6">
        <VBigRadio v-model="confirmCollectivite" :items="[{label: 'Oui', value:'oui'}, {label: 'Non', value:'non'}]">
          Est-ce que l’acte en question concerne bien  <b>{{ collectivite.name }} ({{ region.name }})</b> ?
        </VBigRadio>
      </v-col>
      <v-col cols="12" class="pt-0 pb-2">
        <v-select filled label="Type d'acte" :items="['Délibération de prescription', 'Arrêté', 'Notification aux personnes publiques associées', 'Autre']" />
      </v-col>
      <v-col cols="12" class="pt-0 pb-2">
        <v-text-field filled label="Date de l'acte" type="date" />
      </v-col>
      <v-col cols="12" class="pt-0 pb-2">
        <v-select v-model="acteType" filled placeholder="Selectionner une option" label="Type de document d'urbanisme" :items="['Carte Communale', 'PLU', 'PLUi']" />
      </v-col>
    </v-row>
    <v-row v-if="acteType === 'PLUi'" class="mb-6">
      <v-col cols="11" offset="1">
        <v-row>
          <v-col cols="12" class="pt-0">
            <p>Périmètre de l’acte dans le territoire sélectionné</p>
            <v-btn
              color="primary"
              class="mr-4"
              outlined
              @click="selectAllPerimetre"
            >
              Selectionner toutes
            </v-btn>
            <v-btn
              color="primary"
              outlined
              @click="perimetre = []"
            >
              Déselectionner toutes
            </v-btn>
          </v-col>
          <v-col v-for="(commune, i) in communes" :key="i" cols="4">
            <v-checkbox
              v-model="perimetre"
              hide-details
              class="mt-0"
              :label="`${commune.nom_commune} (${commune.code_commune_INSEE})`"
              :value="commune.code_commune_INSEE"
            />
          </v-col>
          <v-col cols="12" class="my-2">
            <div class="black-border pa-3 d-inline">
              Nombre de communes concernées : <b>{{ perimetre.length }}</b>
            </div>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="11" offset="1">
        <VBigRadio v-model="isPLUiH" :items="[{label: 'Oui', value:'oui'}, {label: 'Non', value:'non'}, {label: 'Je ne sais pas', value:'jsp'}]">
          Tient lieu de PLUiH
        </VBigRadio>
      </v-col>
      <v-col cols="11" offset="1">
        <VBigRadio v-model="isPLUiM" :items="[{label: 'Oui', value:'oui'}, {label: 'Non', value:'non'}, {label: 'Je ne sais pas', value:'jsp'}]">
          Tient lieu de PLUiM (ex PDU)
        </VBigRadio>
      </v-col>
      <v-col v-if="isPLUiM === 'oui'" cols="11" offset="1">
        <VBigRadio v-model="isRequiredPLUiM" :items="[{label: 'Oui', value:'oui'}, {label: 'Non', value:'non'}]">
          Si oui, le PLUiM est-il obligatoire ?
        </VBigRadio>
      </v-col>
      <v-col cols="11" offset="1">
        <VBigRadio v-model="isSCoT" :items="[{label: 'Oui', value:'oui'}, {label: 'Non', value:'non'}, {label: 'Je ne sais pas', value:'jsp'}]">
          Tient lieu de SCoT
        </VBigRadio>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" class="pt-0 pb-2">
        <v-select v-model="typeProcedure" filled placeholder="Selectionner une option" label="Type de procédure" :items="['Principale : E - élaboration','Principale : R - révision', 'Secondaire : RMS - Révision à modalité simplifiée ou Revision allegée', 'Secondaire : M - Modification', 'Secondaire: MS - Modification simplifiée', 'Secondaire : MC - Mise en compatibilité', 'Secondaire : MJ - Mise à jour']" />
      </v-col>
      <v-col cols="12" class="pt-0 pb-2 d-flex align-start">
        <v-text-field v-model="numberProcedure" style="max-width:25%;" filled placeholder="Ex. 4" label="Numéro de procédure" />

        <v-tooltip right>
          <template #activator="{ on, attrs }">
            <v-icon
              color="primary"
              class="ml-4"
              v-bind="attrs"
              v-on="on"
            >
              {{ icons.mdiInformationOutline }}
            </v-icon>
          </template>
          <div>Le numéro est dans l’acte (ex : modification simplifiée : 4)</div>
        </v-tooltip>
      </v-col>
      <v-col cols="12" class="pt-0">
        <VBigRadio v-model="docType" :items="[{label: 'Téléverser un fichier', value:'attachments'}, {label: 'Insérer un lien', value:'link'}]">
          Comment souhaitez-vous déposer votre fichier ?
        </VBigRadio>
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
</template>

<script>
import { mdiUpload, mdiPencil, mdiCheck, mdiAccountSearchOutline, mdiDelete, mdiInformationOutline } from '@mdi/js'
// import axios from 'axios'
import slugify from 'slugify'
import { v4 as uuidv4 } from 'uuid'

export default {
  name: 'PrescriptionsAdd',
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
      confirmCollectivite: null,
      acteType: this.isEpci ? 'PLUi' : null,
      perimetre: [],
      isPLUiH: null,
      isPLUiM: null,
      isRequiredPLUiM: null,
      isSCoT: null,
      typeProcedure: null,
      numberProcedure: '',
      town: null,
      epci: null,
      type: 'commune',
      // loading: true,
      loadingSave: false,
      docType: null,
      link: null,
      files: null,
      icons: {
        mdiUpload,
        mdiPencil,
        mdiCheck,
        mdiAccountSearchOutline,
        mdiInformationOutline,
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
  mounted () {
    this.selectAllPerimetre()
  },
  methods: {
    selectAllPerimetre () {
      this.perimetre = this.communes.map(e => e.code_commune_INSEE)
    },
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
        this.$router.push({ name: 'collectivites-collectiviteId-prescriptions', params: { collectiviteId: this.isEpci ? this.collectivite.EPCI : this.collectivite.code_commune_INSEE }, query: { ...this.$route.query, success: true } })
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

.black-border{
   border: solid 1px var(--v-g800-base);
}
</style>
