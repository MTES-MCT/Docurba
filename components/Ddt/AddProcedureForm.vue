<template>
  <VGlobalLoader v-if="!isLoaded" />
  <validation-observer v-else-if="(procedureCategory === 'principale' || (procedureCategory === 'secondaire' && proceduresParents && proceduresParents.length > 0))" :ref="`observerAddProcedure-${procedureCategory}`" v-slot="{ handleSubmit, invalid }">
    <form @submit.prevent="handleSubmit(createProcedure)">
      <v-container class="pa-0">
        <v-row>
          <v-col cols="12">
            <validation-provider v-slot="{ errors }" name="Type de la procédure" rules="required">
              <v-select
                v-model="typeProcedure"
                style="max-width:50%;"
                :error-messages="errors"
                filled
                placeholder="Selectionner une option"
                label="Type de procédure"
                :items="typesProcedure[procedureCategory]"
              />
            </validation-provider>
          </v-col>
          <v-col cols="12" class="pt-0 pb-2">
            <v-select
              v-model="objetProcedure"
              style="max-width:50%;"
              :hide-details="objetProcedure.includes('Autre')"
              filled
              multiple
              label="Objet de la procédure"
              :items="['Trajectoire ZAN', 'Zones d\'accélération ENR', 'Trait de côte', 'Feu de forêt', 'Autre']"
            />
          </v-col>
          <v-col v-if="objetProcedure.includes('Autre')" cols="12" class="pt-0 pb-2">
            <validation-provider v-slot="{ errors }" name="Details de la procédure" rules="required">
              <v-text-field v-model="otherObjetProcedure" style="max-width:50%;" :error-messages="errors" filled label="Description de l’objet de la procédure" />
            </validation-provider>
          </v-col>
          <v-col v-if="procedureCategory === 'principale'" cols="12">
            <validation-provider v-slot="{ errors }" name="Type de document d'urbanisme" rules="required">
              <v-select
                v-model="typeDu"
                style="max-width:50%;"
                :error-messages="errors"
                filled
                placeholder="Selectionner une option"
                label="Type de document d'urbanisme"
                :items="typesDu"
              />
            </validation-provider>
          </v-col>
          <template v-if="procedureCategory === 'secondaire'">
            <v-col cols="12">
              <validation-provider v-slot="{ errors }" name="Procédure parente" rules="required">
                <v-select
                  v-model="procedureParent"
                  style="max-width:50%;"
                  :error-messages="errors"
                  filled
                  placeholder="Selectionner une option"
                  label="Procédure parente"
                  item-value="id"
                  :items="proceduresParents"
                >
                  <template #selection="{item}">
                    {{ item.type }} du {{ item.doc_type }} {{ item.status }} (collec. porteuse {{ item.collectivite_porteuse_id }})
                  </template>
                  <template #item="{item}">
                    {{ item.type }} du {{ item.doc_type }} {{ item.status }} (collec. porteuse {{ item.collectivite_porteuse_id }})
                  </template>
                </v-select>
              </validation-provider>
            </v-col>
          </template>
          <v-col v-if="procedureCategory === 'secondaire' || typeProcedure === 'Révision'" cols="12" class="d-flex align-start">
            <v-text-field v-model="numberProcedure" style="max-width:50%;" filled placeholder="Ex. 4" label="Numéro de procédure" />
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
        </v-row>
        <DdtPerimeterCheckInput v-model="perimetre" :communes="communes" />
        <v-row>
          <v-col cols="12" class="mt-4 ">
            <div class="mb-2">
              Nom de la procédure
            </div>
            <v-alert v-show="postfixSectoriel" outlined type="info">
              Précisez le titre de votre document sectoriel afin de l’identifier plus facilement dans Docurba.
            </v-alert>
            <div class="d-flex">
              <v-text-field
                :value="baseName"
                background-color="white"
                outlined
                class="rounded-r-0 "
                hide-details
                readonly
              />
              <v-text-field
                v-model="nameComplement"
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
          <v-col cols="12" class="d-flex mt-8">
            <v-btn
              type="submit"
              color="primary"
              depressed
              :loading="loadingSave"
              :disabled="invalid"
            >
              Créer la procédure
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </form>
  </validation-observer>

  <v-container v-else>
    <v-row>
      <v-col cols="12" class="py-12">
        <p class="text-h6">
          Pas de procédure principale
        </p>
        Aucune procédure principale n’a été trouvée pour la collectivité. Une procédure secondaire doit être attachée à une procédure principale.
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mdiInformationOutline } from '@mdi/js'
import axios from 'axios'
import { uniqBy } from 'lodash'
import FormInput from '@/mixins/FormInput.js'

export default {
  name: 'AddProcedureForm',
  mixins: [FormInput],
  props: {
    procedureCategory: {
      type: String,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      loaded: false,
      loadingSave: false,
      typeProcedure: '',
      typesProcedure: {
        principale: ['Elaboration', 'Révision'],
        secondaire: ['Révision à modalité simplifiée ou Révision allégée', 'Modification', 'Modification simplifiée', 'Mise en compatibilité', 'Mise à jour']
      },
      procedureParent: null,
      proceduresParents: null,
      numberProcedure: '',
      objetProcedure: [],
      otherObjetProcedure: '',
      typeDu: '',
      nameComplement: '',
      typesDu: ['CC', 'PLU', 'PLUi', 'PLUiH', 'PLUiM', 'PLUiHM'],
      perimetre: null,
      icons: { mdiInformationOutline }
    }
  },
  computed: {
    procedureParentDocType () {
      return this.proceduresParents?.find(e => e.id === this.procedureParent)?.doc_type
    },
    isLoaded () {
      return this.loaded && (this.procedureCategory === 'principale' || (this.procedureCategory === 'secondaire' && this.proceduresParents !== null))
    },
    postfixSectoriel () {
      return (this.collectivite.type === 'COM' && this.perimetre.length > 1) || (this.collectivite.type !== 'COM' && this.perimetre.length < this.communes.length) ? 'S' : ''
    },
    baseName () {
      return `${this.typeProcedure} ${this.numberProcedure} de ${(this.procedureParent ? this.procedureParentDocType : this.typeDu) + this.postfixSectoriel} ${this.collectivite.intitule}`.replace(/\s+/g, ' ').trim()
    },
    communes () {
      const coms = this.collectivite.membres || this.collectivite.intercommunalite.membres
      return uniqBy(coms, 'code').filter(e => e.type === 'COM')
    }
  },
  async mounted () {
    try {
      if (this.procedureCategory === 'secondaire') {
        const proceduresParents = await this.getProcedures()
        this.proceduresParents = proceduresParents
        if (this.$route.query.secondary_id) {
          this.procedureParent = this.$route.query.secondary_id
        }
      }
      this.perimetre = this.collectivite.type === 'COM' ? [this.collectivite.code] : this.communes.map(e => e.code)
      this.loaded = true
    } catch (error) {
      console.log(error)
    }
  },
  methods: {
    async getProcedures () {
      let query = this.$supabase.from('procedures').select('*').eq('is_principale', true).eq('status', 'opposable')
      let ret = null
      if (this.collectivite.type !== 'COM') {
        query = query.eq('collectivite_porteuse_id', this.collectivite.code)
      } else {
        query = query.contains('current_perimetre', `[{ "inseeCode": "${this.collectivite.code}" }]`)
      }
      const { data: procedures, error } = await query
      ret = procedures
      if (this.collectivite.type !== 'COM') {
        ret = procedures.filter(e => e.current_perimetre.length > 1)
      }
      if (error) { throw error }
      return ret
    },
    async createProcedure () {
      this.loadingSave = true
      try {
        const detailedPerimetre = (await axios({ url: `/api/geo/communes?codes=${this.perimetre}`, method: 'get' })).data
        const fomattedPerimetre = detailedPerimetre.map(e => ({ name: e.intitule, inseeCode: e.code }))

        // const regions = [...new Set(detailedPerimetre.map(e => e.regionCode))]
        const departements = [...new Set(detailedPerimetre.map(e => e.departementCode))]
        let insertedProject = null
        if (this.procedureCategory === 'principale') {
          const insertRet = await this.$supabase.from('projects').insert({
            name: `${this.typeProcedure} ${this.typeDu}`,
            doc_type: this.typeDu,
            region: this.collectivite.regionCode,
            collectivite_id: this.collectivite.intercommunaliteCode || this.collectivite.code,
            current_perimetre: fomattedPerimetre,
            initial_perimetre: fomattedPerimetre,
            collectivite_porteuse_id: this.collectivite.intercommunaliteCode || this.collectivite.code,
            test: true
          }).select()
          console.log('insertedProject: ', insertRet)
          insertedProject = insertRet.data && insertRet.data[0] ? insertRet.data[0].id : null
          if (insertRet.error) { throw insertRet.error }
        }
        await this.$supabase.from('procedures').insert({
          secondary_procedure_of: this.procedureParent,
          type: this.typeProcedure,
          commentaire: this.objetProcedure && this.objetProcedure.includes('Autre') ? this.objetProcedure?.join(', ') + ' - ' + this.otherObjetProcedure : this.objetProcedure?.join(', '),
          collectivite_porteuse_id: this.collectivite.intercommunaliteCode || this.collectivite.code,
          is_principale: this.procedureCategory === 'principale',
          status: 'en cours',
          is_sectoriel: null,
          is_scot: null,
          is_pluih: this.typeDu === 'PLUiH',
          is_pdu: null,
          doc_type: this.procedureCategory === 'principale' ? this.typeDu : this.procedureParentDocType,
          departements,
          numero: this.procedureCategory === 'principale' ? '1' : this.numberProcedure,
          current_perimetre: fomattedPerimetre,
          initial_perimetre: fomattedPerimetre,
          project_id: insertedProject,
          name: (this.baseName + ' ' + this.nameComplement).trim(),
          owner_id: this.$user.id,
          testing: true
        })
        this.$router.push(`/ddt/${this.collectivite.departementCode}/collectivites/${this.collectivite.code}/${this.collectivite.code.length > 5 ? 'epci' : 'commune'}`)
      } catch (error) {
        this.error = error
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
