<template>
  <VGlobalLoader v-if="!isLoaded" />
  <validation-observer v-else :ref="`observerUpdateProcedure`" v-slot="{ handleSubmit, invalid }">
    <form @submit.prevent="handleSubmit(updateProcedure)">
      <v-container class="pa-0">
        <div class="d-flex justify-end pb-4">
          <SignalementProbleme />
        </div>
        <v-row>
          <v-col cols="6">
            <validation-provider v-slot="{ errors }" name="Type de la procédure" rules="required">
              <v-select
                v-model="procedureType"
                :error-messages="errors"
                filled
                placeholder="Selectionner une option"
                label="Type de procédure"
                :items="typeProcedureSelectValues"
              />
            </validation-provider>
          </v-col>
          <v-col cols="4">
            <p class="pt-3">
              <v-icon color="primary">
                {{ icons.mdiInformationOutline }}
              </v-icon>
              <a
                href="https://docurba.crisp.help/fr/article/comment-bien-choisir-sa-procedure-pour-faire-evoluer-son-document-durbanisme-plu-xku87n/"
                target="_blank"
              >
                Comment choisir le type de procédure</a>
              <v-icon color="primary">
                {{ icons.mdiOpenInNew }}
              </v-icon>
            </p>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6" class="pt-0 pb-2">
            <v-select
              v-model="procedureCommentaire"
              :hide-details="procedureCommentaire.includes('Autre')"
              filled
              multiple
              label="Objet de la procédure"
              :items="procedureCommentaireSelectValues"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col v-if="procedureCommentaire.includes('Autre')" cols="6" class="pt-0 pb-2">
            <validation-provider v-slot="{ errors }" name="Details de la procédure" rules="required">
              <v-text-field v-model="procedureCommentaireAutre" :error-messages="errors" filled label="Description de l’objet de la procédure" />
            </validation-provider>
          </v-col>
        </v-row>
        <v-row>
          <v-col v-if="procedure.is_principale" cols="6">
            <validation-provider v-slot="{ errors }" name="Type de document d'urbanisme" rules="required">
              <v-select
                v-model="procedureDocType"
                :error-messages="errors"
                filled
                placeholder="Selectionner une option"
                label="Type de document d'urbanisme"
                :items="procedureTypeDocSelectValues"
              />
            </validation-provider>
          </v-col>
        </v-row>
        <v-row v-if="procedure.secondary_procedure_of || procedureType === 'Révision'">
          <v-col cols="6" class="d-flex align-start">
            <v-text-field v-model="procedureNumero" filled placeholder="Ex. 4" label="Numéro de procédure" />
          </v-col>
          <v-col cols="6">
            <p>
              <v-icon color="primary">
                {{ icons.mdiInformationOutline }}
              </v-icon>
              Le numéro est dans l’acte
              <br>
              ex : pour une modification simplifiée n°4, saisir <strong>4</strong>
            </p>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <v-alert v-show="postfixSectoriel" outlined type="info">
              Précisez le titre de votre document sectoriel afin de l’identifier plus facilement dans Docurba.
            </v-alert>
            <div class="d-flex">
              <v-text-field
                v-model="procedureName"
                hide-details
                label="Nom"
                class="rounded-r-0"
                filled
                disabled
              />
              <v-text-field
                v-model="procedureNameComplement"
                hide-details
                label="Complément (optionnel)"
                class="rounded-l-0 smaller-input-slot"
                placeholder="Précisez le titre de la procédure (optionnel)"
                filled
              />
            </div>
            <div class="caption mt-1">
              Ce nom n’a pas de valeur légale et sera utilisé pour retrouver vos procédures dans Docurba.
            </div>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <DashboardDUModalPerimetre :perimetres="communes" info-banner-message="Pour modifier le périmètre, contactez-nous en cliquant sur « Signaler un problème »." show-help="true" />
            <SignalementProbleme />
          </v-col>
        </v-row>
          <v-col cols="12" class="d-flex">
            <v-btn
              type="submit"
              color="primary"
              depressed
              :loading="loadingSave"
              :disabled="invalid"
            >
              Modifier la procédure
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </form>
  </validation-observer>
</template>

<script>
import { mdiInformationOutline, mdiOpenInNew } from '@mdi/js'
import axios from 'axios'
import FormInput from '@/mixins/FormInput.js'

export default {
  name: 'UpdateProcedureForm',
  mixins: [FormInput],
  props: {
    procedureId: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      // Form data
      procedureCommentaire: '',
      procedureCommentaireAutre: '',
      procedureNameComplement: '',
      procedureNumero: '',
      procedureType: '',
      procedureDocType: '',
      procedureParent: null,

      // Other
      collectivite: '',
      codesCommune: null,
      communes: null,
      procedureCommentaireSelectValues: ['Trajectoire ZAN', 'Zones d\'accélération ENR', 'Trait de côte', 'Feu de forêt', 'Autre'],
      procedureTypeDocSelectValues: ['CC', 'PLU', 'PLUi', 'PLUiH', 'PLUiM', 'PLUiHM', 'SCOT'],
      icons: { mdiInformationOutline, mdiOpenInNew },
      loaded: false,
      loadingSave: false
    }
  },
  computed: {
    procedureName () {
      return this.baseName()
    },
    // Form data
    computedProcedureName () {
      return `${this.procedureName} ${this.procedureNameComplement}`
    },

    // Other
    postfixSectoriel () {
      return (this.collectivite.type === 'COM' && this.codesCommune.length > 1) || (this.collectivite.type !== 'COM' && this.codesCommune.length < this.communes.length) ? 'S' : ''
    },
    typeProcedureSelectValues () {
      if (this.procedure.is_principale) {
        return ['Elaboration', 'Révision']
      } else {
        return ['Révision à modalité simplifiée ou Révision allégée', 'Modification', 'Modification simplifiée', 'Mise en compatibilité', 'Mise à jour']
      }
    },
    typeCompetence () {
      return this.typeDu === 'SCOT' ? 'competenceSCOT' : 'competencePLU'
    },
    isLoaded () {
      return this.loaded && (this.procedure.is_principale || this.procedureParent !== null)
    }
  },
  async mounted () {
    try {
      const { data: resultProcedure } = await this.$supabase.from('procedures')
        .select('id, commentaire, owner_id, secondary_procedure_of, doc_type, type, numero, name, is_principale, collectivite_porteuse_id, secondary_procedure_of(name, doc_type), procedures_perimetres(collectivite_code)')
        .eq('id', this.procedureId)
      const procedure = resultProcedure[0]

      const { data: collectivite } = await axios(`/api/geo/collectivites/${procedure.collectivite_porteuse_id}`)

      const codes = procedure.procedures_perimetres?.map(commune => commune.collectivite_code)
      const communes = (await axios({ url: `/api/geo/communes?codes=${codes}`, method: 'get' })).data

      this.loaded = true
      this.procedure = procedure
      this.communes = communes
      this.collectivite = collectivite
      this.codesCommune = communes.map(e => e.code)
      this.procedureParent = this.procedure.secondary_procedure_of
      this.procedureType = this.procedure.type
      this.procedureDocType = this.procedure.doc_type
      this.procedureNumero = this.procedure.numero
      if (this.procedure.commentaire) {
        const procedureObjects = this.procedure.commentaire.split(',')
        const selectedObjects = []
        for (let index = 0; index < procedureObjects.length; index++) {
          const element = procedureObjects[index]
          if (this.procedureCommentaireSelectValues.includes(element)) {
            selectedObjects.push(element)
            procedureObjects.splice(index, 1)
          }
        }
        this.procedureCommentaire = selectedObjects
        this.procedureCommentaireAutre = procedureObjects
        if (this.procedure.name) {
          // Try to strip name
          // TODO: what if the original name does not match the new this.baseName?
          const complement = this.procedure.name.replace(new RegExp(`^.*${this.collectivite.intitule} `, 'g'), '')
          this.procedureNameComplement = complement
        }
      }
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error)
    }
  },
  methods: {
    baseName () {
      // We could use $utils.formatProcedureName but it does not accept single arguments.
      // It would break the reactivity.
      return `${this.procedureType} ${this.procedureNumero} de ${(this.procedureParent ? this.procedureParent.doc_type : this.procedureDocType) + this.postfixSectoriel} ${this.collectivite.intitule}`.replace(/\s+/g, ' ').trim()
    },
    async updateProcedure () {
      this.loadingSave = true

      try {
        if (this.procedure.is_principale === 'principale') {
          const { error } = await this.$supabase.from('projects').update({
            name: `${this.procedureType} ${this.procedureDocType}`,
            doc_type: this.procedureDocType
          }).eq('id', this.procedure.project_id).select()

          if (error) {
            // eslint-disable-next-line no-console
            console.log('Error updating the project')
            throw error
          }
        }

        // This will be replaced anyway.
        let commentaire = this.procedureCommentaire?.join(', ')
        if (commentaire && commentaire.includes('Autre')) {
          commentaire = commentaire + ' - ' + this.procedureCommentaireAutre
        }
        const { error } = await this.$supabase.from('procedures').update({
          // current_perimetre: oldFomattedPerimetre,
          type: this.procedureType,
          is_scot: this.procedureType === 'SCOT',
          is_pluih: this.procedureType === 'PLUiH',
          doc_type: this.procedureDocType,
          numero: this.procedureNumero ? this.procedureNumero : '',
          name: this.computedProcedureName,
          commentaire
        }).eq('id', this.procedure.id).select()

        if (error) {
          // eslint-disable-next-line no-console
          console.log('errorInsertedProcedure: ', error)
        }

        this.$analytics({
          category: 'procedures',
          name: 'update_procedure',
          value: (this.procedure.name)
        })

        this.$router.back()
      } catch (error) {
        this.error = error
        // eslint-disable-next-line no-console
        console.log(error)
      } finally {
        this.loadingSave = false
      }
    }
  }

}
</script>

<style lang="scss">
.smaller-input-slot .v-input__slot{
  min-height: 55px !important;
}
</style>
