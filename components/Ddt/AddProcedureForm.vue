<template>
  <validation-observer :ref="`observerAddProcedure-${procedureCategory}`" v-slot="{ handleSubmit, invalid }">
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
          <v-col cols="12">
            <v-text-field v-model="description" filled placeholder="Description de l’objet de la procédure" label="Description de l’objet de la procédure" />
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
                  v-model="typeDu"
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
            <v-col cols="12" class="d-flex align-start">
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
          </template>
        </v-row>
        <DdtPerimeterCheckInput v-model="perimetre" :communes="collectivite.communes || collectivite.intercommunalite.communes" />
        <v-row>
          <v-col cols="12" class="d-flex">
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
</template>

<script>
import { mdiInformationOutline } from '@mdi/js'
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
      loadingSave: false,
      typeProcedure: '',
      typesProcedure: {
        principale: ['Élaboration', 'Révision'],
        secondaire: ['Révision à modalité simplifiée ou Révision allégée', 'Modification', 'Modification simplifiée', 'Mise en comptabilité', 'Mise à jour']
      },
      proceduresParents: [],
      numberProcedure: '',
      description: '',
      typeDu: '',
      typesDu: ['Carte Communale', 'PLU', 'PLUi', 'PLUiH', 'PLUiM'],
      perimetre: this.collectivite.type === 'Commune' ? [this.collectivite.code] : this.collectivite.intercommunalite.communes.map(e => e.code),
      icons: {
        mdiInformationOutline
      }
    }
  },
  async mounted () {
    try {
      if (this.procedureCategory === 'secondaire') {
        this.proceduresParents = await this.getProcedures()
      }
    } catch (error) {
      console.log()
    }
  },
  methods: {
    async getProcedures () {
      console.log('this.$route.collectiviteId: ', this.$route.params.collectiviteId)
      const { data: procedures, error } = await this.$supabase.from('procedures').select('*')
        .eq('is_principale', true)
        .contains('current_perimetre', '[{ "inseeCode": "73001" }]')
      console.log('procedures: ', procedures)
      if (error) { throw error }
      return procedures
    }
  },
  createProcedure () {
    console.log('Procedure created')
  }
}
</script>
