<template>
  <VGlobalLoader v-if="!isLoaded" />
  <validation-observer v-else-if="(procedureCategory === 'principale' || (procedureCategory === 'secondaire' && proceduresParents && proceduresParents.length > 0))" :ref="`observerAddProcedure-${procedureCategory}`" v-slot="{ handleSubmit, invalid }">
    <form @submit.prevent="handleSubmit(createProcedure)">
      <v-container class="pa-0">
        <v-row>
          <v-col cols="6">
            <validation-provider v-slot="{ errors }" name="Type de la procédure" rules="required">
              <v-select
                v-model="typeProcedure"
                :error-messages="errors"
                filled
                placeholder="Selectionner une option"
                label="Type de procédure"
                :items="typesProcedure[procedureCategory]"
              />
            </validation-provider>
          </v-col>
          <v-col cols="6">
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
              v-model="objetProcedure"
              :hide-details="objetProcedure.includes('Autre')"
              filled
              multiple
              label="Objet de la procédure"
              :items="['Trajectoire ZAN', 'Zones d\'accélération ENR', 'Trait de côte', 'Feu de forêt', 'Autre']"
            />
          </v-col>
        </v-row>
        <v-row>
          <v-col v-if="objetProcedure.includes('Autre')" cols="6" class="pt-0 pb-2">
            <validation-provider v-slot="{ errors }" name="Details de la procédure" rules="required">
              <v-text-field v-model="otherObjetProcedure" :error-messages="errors" filled label="Description de l’objet de la procédure" />
            </validation-provider>
          </v-col>
        </v-row>
        <v-row>
          <v-col v-if="procedureCategory === 'principale'" cols="6">
            <validation-provider v-slot="{ errors }" name="Type de document d'urbanisme" rules="required">
              <v-select
                v-model="typeDu"
                :error-messages="errors"
                filled
                placeholder="Selectionner une option"
                label="Type de document d'urbanisme"
                :items="typesDu"
              />
            </validation-provider>
          </v-col>
        </v-row>
        <v-row>
          <template v-if="procedureCategory === 'secondaire'">
            <v-col cols="6">
              <validation-provider v-slot="{ errors }" name="Procédure parente" rules="required">
                <v-select
                  v-model="procedureParent"
                  :error-messages="errors"
                  filled
                  placeholder="Selectionner une option"
                  label="Procédure parente"
                  item-value="id"
                  :items="proceduresParents"
                >
                  <template #selection="{item}">
                    {{ $utils.formatProcedureName(item, item.porteuse) }}
                  </template>
                  <template #item="{item}">
                    {{ $utils.formatProcedureName(item, item.porteuse) }}
                  </template>
                </v-select>
              </validation-provider>
            </v-col>
          </template>
        </v-row>
        <v-row v-if="procedureCategory === 'secondaire' || typeProcedure === 'Révision'">
          <v-col cols="6" class="d-flex align-start">
            <v-text-field v-model="numberProcedure" filled placeholder="Ex. 4" label="Numéro de procédure" />
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
        <DdtPerimeterCheckInput
          v-if="procedureCategory === 'principale'"
          v-model="perimetre"
          :communes="communes"
        />
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
import { mdiInformationOutline, mdiOpenInNew } from '@mdi/js'
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
      typesDu: ['CC', 'PLU', 'PLUi', 'PLUiH', 'PLUiM', 'PLUiHM', 'SCOT'],
      perimetre: null,
      icons: { mdiInformationOutline, mdiOpenInNew }
    }
  },
  computed: {
    typeCompetence () {
      return this.typeDu === 'SCOT' ? 'competenceSCOT' : 'competencePLU'
    },
    collectivitePorteuseCode () {
      if (this.collectivite[this.typeCompetence]) {
        // return the collectivite if it has the competence
        return this.collectivite.code
      } else if (this.collectivite.intercommunalite) {
        // return the interco if it exist.
        return this.collectivite.intercommunalite.code
      } else {
        // Return the collectivite code if there is no groupement available.
        // This can create an anomaly with Banatic but is better than nothing.
        return this.collectivite.code
      }
    },
    procedureParentObj () {
      return this.proceduresParents?.find(e => e.id === this.procedureParent)
    },
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
      const uniqComs = uniqBy(coms, 'code').filter(e => e.type === 'COM')

      if (this.collectivite.code.length < 6) {
        uniqComs.push(this.collectivite)
      }

      return uniqComs
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
      // eslint-disable-next-line no-console
      console.log(error)
    }
  },
  methods: {
    async getProcedures () {
      let query = this.$supabase.from('procedures').select('*, procedures_perimetres(*)').eq('is_principale', true).eq('status', 'opposable')

      if (this.collectivite.type !== 'COM') {
        query = query.eq('collectivite_porteuse_id', this.collectivite.code)
      } else {
        query = query.contains('current_perimetre', `[{ "inseeCode": "${this.collectivite.code}" }]`)
      }

      const { data: procedures, error } = await query

      if (error) {
        // eslint-disable-next-line no-console
        console.log('error getProcedures', error)
      }

      const collectiviteCodes = new Set(procedures.flatMap(p => [
        p.collectivite_porteuse_id,
        ...p.procedures_perimetres.map(c => c.collectivite_code)
      ]))

      const { data: collectivites } = await axios({
        url: '/api/geo/collectivites',
        params: new URLSearchParams(collectiviteCodes.map(code => ['codes', code]))
      })

      const enrichedProcedures = procedures.map((p) => {
        const comd = p.procedures_perimetres.find(c => c.collectivite_type === 'COMD')

        const collectivite = collectivites.find((c) => {
          if (comd) {
            return c.code === comd.collectivite_code && c.type === 'COMD'
          } else if (p.procedures_perimetres.length === 1) {
            return c.code === p.procedures_perimetres[0].collectivite_code
          } else { return c.code === p.collectivite_porteuse_id }
        })

        if (comd) {
          collectivite.intitule += ' COMD'
        }

        return {
          porteuse: collectivites.find(c => c.code === p.collectivite_porteuse_id),
          collectivite,
          ...p
        }
      })

      if (this.collectivite.type !== 'COM') {
        return enrichedProcedures.filter(e => e.current_perimetre.length > 1)
      } else {
        return enrichedProcedures
      }
    },
    async createProcedure () {
      this.loadingSave = true

      try {
        let perimetre
        if (this.procedureParent) {
          perimetre = this.procedureParentObj.procedures_perimetres.map(perim => perim.collectivite_code)
        } else {
          perimetre = this.perimetre
        }
        const detailedPerimetre = (await axios({ url: `/api/geo/communes?codes=${perimetre}`, method: 'get' })).data
        const oldFomattedPerimetre = detailedPerimetre.map(e => ({ name: e.intitule, inseeCode: e.code }))
        const departements = [...new Set(detailedPerimetre.map(e => e.departementCode))]
        let insertedProject = null

        if (this.procedureCategory === 'principale') {
          const insertRet = await this.$supabase.from('projects').insert({
            name: `${this.typeProcedure} ${this.typeDu}`,
            doc_type: this.typeDu,
            region: this.collectivite.regionCode,
            current_perimetre: oldFomattedPerimetre,
            collectivite_id: this.collectivite.intercommunaliteCode || this.collectivite.code,
            collectivite_porteuse_id: this.collectivitePorteuseCode,
            test: true,
            owner: this.$user.id
          }).select()

          insertedProject = insertRet.data && insertRet.data[0] ? insertRet.data[0].id : null
          if (insertRet.error) { throw insertRet.error }
        }

        const { data: insertedProcedure, error: errorInsertedProcedure } = await this.$supabase.from('procedures').insert({
          shareable: true,
          secondary_procedure_of: this.procedureParent,
          type: this.typeProcedure,
          commentaire: this.objetProcedure && this.objetProcedure.includes('Autre') ? this.objetProcedure?.join(', ') + ' - ' + this.otherObjetProcedure : this.objetProcedure?.join(', '),
          collectivite_porteuse_id: this.collectivitePorteuseCode,
          is_principale: this.procedureCategory === 'principale',
          status: 'en cours',
          is_sectoriel: null,
          is_scot: this.typeDu === 'SCOT',
          is_pluih: this.typeDu === 'PLUiH',
          is_pdu: null,
          current_perimetre: oldFomattedPerimetre,
          doc_type: this.procedureCategory === 'principale' ? this.typeDu : this.procedureParentDocType,
          departements,
          numero: this.procedureCategory === 'principale' ? '1' : this.numberProcedure,
          project_id: insertedProject,
          name: (this.baseName + ' ' + this.nameComplement).trim(),
          owner_id: this.$user.id,
          testing: true
        }).select()

        if (errorInsertedProcedure) {
          // eslint-disable-next-line no-console
          console.log('errorInsertedProcedure: ', errorInsertedProcedure)
        }

        const fomattedPerimetre = detailedPerimetre.map(e => ({ collectivite_code: e.code, collectivite_type: e.type, procedure_id: insertedProcedure[0].id, opposable: false, departement: e.departementCode }))
        await this.$supabase.from('procedures_perimetres').insert(fomattedPerimetre)

        const sender = {
          user_email: this.$user.email,
          project_id: insertedProject ?? this.proceduresParents?.find(e => e.id === this.procedureParent)?.project_id,
          shared_by: this.$user.id,
          notified: false,
          role: 'write_frise',
          archived: false,
          dev_test: true
        }

        // console.log('this.proceduresParents?.find(e => e.id === this.procedureParent): ', this.proceduresParents?.find(e => e.id === this.procedureParent))
        // console.log('sender SHARING: ', sender)

        const { error: errorInsertedCollabs } = await this.$supabase.from('projects_sharing').insert(sender)

        if (errorInsertedCollabs) {
          // eslint-disable-next-line no-console
          console.log('errorInsertedCollabs: ', errorInsertedCollabs)
        }

        this.$analytics({
          category: 'procedures',
          name: 'create_procedure',
          value: (this.baseName + ' ' + this.nameComplement).trim()
        })

        this.$router.push(`/frise/${insertedProcedure[0].id}/invite`)
        // this.$router.push(`/ddt/${this.collectivite.departementCode}/collectivites/${this.collectivite.code}/${this.collectivite.code.length > 5 ? 'epci' : 'commune'}`)
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
