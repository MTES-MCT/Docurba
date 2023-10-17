<template>
  <v-container id="prescription">
    <v-row align="end">
      <v-col cols="auto">
        <h2>Actes</h2>
      </v-col>
      <v-col>
        <DashboardCollectivitesInnerNav :is-epci="isEpci" :collectivite="collectivite" :communes="communes" />
      </v-col>
    </v-row>

    <PrescriptionYouWantCard />

    <v-alert v-if="error" type="error">
      {{ error }}
    </v-alert>
    <validation-observer ref="observerActePrescription" v-slot="{ handleSubmit }">
      <form @submit.prevent="handleSubmit(submitPrescription)">
        <v-row>
          <v-col cols="12" class="mb-6">
            <validation-provider v-slot="{ errors }" name="Vérification" rules="required|needToBeOui">
              <VBigRadio v-model="confirmCollectivite" :error-messages="errors" :items="[{label: 'Oui', value:'oui'}, {label: 'Non', value:'non'}]">
                Est-ce que l’acte en question concerne bien  <b>{{ collectivite.intitule }} ({{ collectivite.region.intitule }})</b> ?
              </VBigRadio>
            </validation-provider>
          </v-col>
          <v-col cols="12" class="pt-0 pb-2">
            <validation-provider v-slot="{ errors }" name="Type d'acte" rules="required">
              <v-select v-model="acteType" :error-messages="errors" filled label="Type d'acte" :items="['Délibération de prescription', 'Délibération du débat sur le PADD', 'Délibération d\'arrêt du projet', 'Délibération de lancement de l\'enquête publique', 'Délibération d\'approbation', 'Arrêté de lancement de la procédure', 'Notification aux personnes publiques associées', 'Autre']" />
            </validation-provider>
          </v-col>
          <v-col v-if="acteType === 'Autre'" offset="1" cols="11" class="pt-0 pb-2">
            <validation-provider v-slot="{ errors }" name="Details de l'acte" rules="required">
              <v-text-field v-model="otherActeType" :error-messages="errors" filled label="Précisez" />
            </validation-provider>
          </v-col>
          <v-col cols="12" class="pt-0 pb-2">
            <validation-provider v-slot="{ errors }" name="Date de l'acte" rules="required">
              <v-text-field v-model="date" :error-messages="errors" filled label="Date de l'acte" type="date" />
            </validation-provider>
          </v-col>
          <v-col cols="12" class="pt-0 pb-2">
            <validation-provider v-slot="{ errors }" name="Type du DU" rules="required">
              <v-select
                v-model="DUType"
                :error-messages="errors"
                filled
                placeholder="Selectionner une option"
                label="Type de document d'urbanisme"
                :items="['Carte Communale', 'PLU', 'PLUi']"
              />
            </validation-provider>
          </v-col>
        </v-row>
        <v-row v-if="isEpci" class="mb-6">
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
                  :label="`${commune.intitule} (${commune.code})`"
                  :value="commune.code"
                />
              </v-col>
              <v-col cols="12" class="my-2">
                <div class="black-border pa-3 d-inline">
                  Nombre de communes concernées : <b>{{ perimetre.length }}</b>
                </div>
              </v-col>
            </v-row>
          </v-col>
          <template v-if="DUType === 'PLUi'">
            <v-col cols="11" offset="1">
              <validation-provider v-slot="{ errors }" name="Status PLUiH" rules="required">
                <VBigRadio v-model="isPLUiH" :error-messages="errors" :items="[{label: 'Oui', value:'oui'}, {label: 'Non', value:'non'}, {label: 'Je ne sais pas', value:'jsp'}]">
                  Tient lieu de PLUiH
                </VBigRadio>
              </validation-provider>
            </v-col>
            <v-col cols="11" offset="1">
              <validation-provider v-slot="{ errors }" name="Status PLUiM" rules="required">
                <VBigRadio v-model="isPLUiM" :error-messages="errors" :items="[{label: 'Oui', value:'oui'}, {label: 'Non', value:'non'}, {label: 'Je ne sais pas', value:'jsp'}]">
                  Tient lieu de PLUiM (ex PDU)
                </VBigRadio>
              </validation-provider>
            </v-col>
            <v-col v-if="isPLUiM === 'oui'" cols="11" offset="1">
              <validation-provider v-slot="{ errors }" name="Obligation du PLUiM" rules="required">
                <VBigRadio v-model="isRequiredPLUiM" :error-messages="errors" :items="[{label: 'Oui', value:'oui'}, {label: 'Non', value:'non'}]">
                  Si oui, le PLUiM est-il obligatoire ?
                </VBigRadio>
              </validation-provider>
            </v-col>
            <v-col cols="11" offset="1">
              <validation-provider v-slot="{ errors }" name="Status SCoT" rules="required">
                <VBigRadio v-model="isSCoT" :error-messages="errors" :items="[{label: 'Oui', value:'oui'}, {label: 'Non', value:'non'}, {label: 'Je ne sais pas', value:'jsp'}]">
                  Tient lieu de SCoT
                </VBigRadio>
              </validation-provider>
            </v-col>
          </template>
        </v-row>
        <v-row>
          <v-col cols="12" class="pt-0 pb-2">
            <validation-provider v-slot="{ errors }" name="Type de la procédure" rules="required">
              <v-select
                v-model="typeProcedure"
                :error-messages="errors"
                filled
                placeholder="Selectionner une option"
                label="Type de procédure"
                :items="typesProcedure"
              />
            </validation-provider>
          </v-col>
          <v-col cols="12" class="pt-0 pb-2">
            <v-select v-model="MSScope" filled multiple label="Cette procédure concerne" :items="['Trajectoire ZAN', 'Zones d\'accélération ENR', 'Trait de côte', 'Feu de forêt', 'Autre']" />
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
              <div>Le numéro est dans l’acte (ex : modification simplifiée n°4)</div>
            </v-tooltip>
          </v-col>
          <v-col cols="12" class="pt-0">
            <validation-provider v-slot="{ errors }" name="Choix du mode de transmission" rules="required">
              <VBigRadio v-model="docType" :error-messages="errors" :items="[{label: 'Téléverser un fichier', value:'attachments'}, {label: 'Insérer un lien', value:'link'}]">
                Comment souhaitez-vous déposer votre fichier ?
              </VBigRadio>
            </validation-provider>
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
            <validation-provider v-slot="{ errors }" name="URL du document" rules="required">
              <v-text-field
                ref="urlTextfield"
                v-model="link"
                :error-messages="errors"
                filled
                placeholder="documentprescription.com"
                :rules="urlRules"
              />
            </validation-provider>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" class="d-flex mb-16">
            <v-btn
              type="submit"
              color="primary"
              depressed
              :loading="loadingSave"
            >
              {{ docType === 'link'? 'Lier le document' : 'Déposer' }}
            </v-btn>
          </v-col>
        </v-row>
      </form>
    </validation-observer>
  </v-container>
</template>

<script>
import { mdiUpload, mdiPencil, mdiCheck, mdiAccountSearchOutline, mdiDelete, mdiInformationOutline } from '@mdi/js'
import axios from 'axios'
import { v4 as uuidv4 } from 'uuid'
import FormInput from '@/mixins/FormInput.js'

export default {
  name: 'PrescriptionsAdd',
  mixins: [FormInput],
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
      error: null,
      typesProcedure: [{ header: 'Principale' }, { text: 'E - élaboration' }, { text: 'R - révision' }, { divider: true }, { header: 'Secondaire' }, { text: 'RMS - Révision à modalité simplifiée ou Revision allegée' }, { text: 'M - Modification' }, { text: 'MS - Modification simplifiée' }, { text: 'MC - Déclaration préalable valant mise en compatibilité' }, { text: 'MJ - Mise à jour' }],
      confirmCollectivite: null,
      DUType: this.isEpci ? 'PLUi' : null,
      acteType: null,
      otherActeType: null,
      date: null,
      perimetre: this.isEpci ? [] : [this.$route.collectiviteId],
      isPLUiH: null,
      isPLUiM: null,
      isRequiredPLUiM: null,
      isSCoT: null,
      typeProcedure: null,
      MSScope: [],
      numberProcedure: '',
      town: null,
      epci: null,
      type: 'commune',
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
    },
    validationErrors () {
      return this.$refs?.observerActePrescription?.errors
    }
  },
  watch: {
    validationErrors (newVal) {
      // console.log('TRIGGER')
    },
    DUType (newVal) {
      if (newVal === 'PLUi') {
        this.selectAllPerimetre()
      } else {
        this.perimetre = []
      }
    }
  },
  mounted () {
    this.$watch(() => this.$refs.observerActePrescription.flags.failed, (val) => {
      if (val) {
        this.$nextTick(() => {
          const el = this.$el.querySelector('.error--text:first-of-type')
          this.$vuetify.goTo(el)
        })
      }
    })

    // console.log('this.$refs: ', this.$refs)
    this.selectAllPerimetre()
  },
  methods: {
    selectAllPerimetre () {
      this.perimetre = this.communes.map(c => c.code)
    },
    removeFile (file) {
      this.files = [...this.files].filter(e => e !== file)
    },
    setFiles (files) {
      this.files = files
    },

    async uploadFiles () {
      if (this.files?.length) {
        const uploadTimestamp = Date.now()
        const filesData = []
        for (let fileIndex = 0; fileIndex < this.files.length; fileIndex++) {
          const file = this.files[fileIndex]
          // <type_epci_commune>/<insee_or_code>/<date>/files
          const idFile = uuidv4()
          const path = `${this.isEpci ? 'epci' : 'commune'}/${this.$route.params.collectiviteId}/${uploadTimestamp}/${idFile}`
          // console.log('path: ', path)
          const { data: dataUpload, error } = await this.$supabase.storage
            .from('prescriptions')
            .upload(path, file)
          if (error) {
            // eslint-disable-next-line no-console
            console.log('error on upload: ', error)
            throw new Error('Erreur d\'upload')
          }

          const { data: dataUrl, error: errorUrl } = this.$supabase.storage.from('prescriptions').getPublicUrl(dataUpload.path)
          if (errorUrl) { throw new Error('Erreur de récuparation de l\'url') }
          filesData.push({ path, name: file.name, id: uuidv4(), url: dataUrl.publicUrl })
          // console.log('TEST DATA: ', filesData)
        }

        return filesData
      } else {
        throw new Error('Pas de fichier à téléverser')
      }
    },

    async submitPrescription () {
      try {
        await this.$user.isReady
        // console.log('submitPrescription')
        this.loadingSave = true

        // TODO: Add column verified or accepted sur les prescription with fill automatically if the user posting is a verified connected one.
        const prescription = {
          epci: this.isEpci ? this.collectivite : null,
          towns: this.isEpci ? this.collectivite.communes.map(e => e.code) : [this.collectivite.code],
          attachments: null,
          type: this.docType,
          acte_type: this.acteType,
          other_acte_type: this.otherActeType,
          date: this.date,
          du_type: this.DUType,
          perimetre: this.perimetre,
          is_pluih: this.isPLUiH,
          is_pluim: this.isPLUiM,
          mandatory_pluim: this.isRequiredPLUiM,
          is_scot: this.isSCoT,
          procedure_type: this.typeProcedure,
          ms_scope: this.MSScope,
          procedure_number: this.numberProcedure,
          user_id: this.$user.id || null
        }
        if (this.docType === 'link') {
          prescription.link_url = this.link
        } else if (this.docType === 'attachments') {
          prescription.attachments = await this.uploadFiles()
        }
        await this.$supabase.from('prescriptions').insert([prescription])
        this.loadingSave = false

        const userData = {
          email: this.$user?.email || this.$route.query.email,
          // region: this.collectivite.region.name,
          collectivite: this.collectivite,
          isEpci: this.isEpci,
          attachements: prescription.attachments || [{ name: 'lien', url: prescription.link_url }]
        }
        await axios({
          url: '/api/slack/notify/admin/acte',
          method: 'post',
          data: { userData }
        })

        axios({
          url: '/api/pipedrive/depot_acte',
          method: 'post',
          data: { userData }
        })
        // console.log('REDIRECT')

        this.$analytics({
          category: 'prescriptions',
          name: 'ajout',
          value: this.collectivite.code,
          data: {
            collectivite: this.collectivite
          }
        })

        this.$router.push({
          name: 'collectivites-collectiviteId-prescriptions',
          params: { collectiviteId: this.collectivite.code },
          query: { ...this.$route.query, success: true }
        })
      } catch (error) {
        this.error = error
        this.$vuetify.goTo('error--text:first-of-type')
        this.loadingSave = false
        // eslint-disable-next-line no-console
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
