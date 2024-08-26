<template>
  <div class="pt-7">
    <v-data-table
      v-if="steps.length > 0"
      :headers="headers"
      :items="steps"
      hide-default-footer
      :items-per-page="-1"
      class="elevation-0 mb-7"
    >
      <template #item="{item, index}">
        <tr v-if="item.edit">
          <td colspan="100%">
            <FriseDgdStepForm />
          </td>
        </tr>
        <tr v-else>
          <td>{{ item.name }}</td>
          <td>{{ item.amount }}</td>
          <td>{{ item.isDone }}</td>
          <td>{{ item.date }}</td>
          <td>{{ item.category }}</td>
          <td class="d-flex align-center justify-end">
            <v-menu
              bottom
              left
            >
              <template #activator="{ on, attrs }">
                <v-btn
                  class="rounded"
                  outlined
                  color="primary"
                  icon
                  tile
                  v-bind="attrs"
                  v-on="on"
                >
                  <v-icon>{{ icons.mdiDotsVertical }}</v-icon>
                </v-btn>
              </template>

              <v-list>
                <v-list-item @click="editLine(item, index)">
                  <v-list-item-title>Éditer l'étape</v-list-item-title>
                </v-list-item>
                <v-list-item @click="deleteItem(item, index)">
                  <v-list-item-title class="error--text">
                    Supprimer l'étape
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </td>
        </tr>
      </template>
    </v-data-table>
    <v-row v-if="showStepForm">
      <v-col cols="12" class="d-flex">
        <FriseDgdStepForm @cancel="showStepForm = false" @save="saveStep(arguments[0])" />
      </v-col>
    </v-row>
    <div v-else>
      <v-btn class="mb-4" outlined color="primary" @click="showStepForm = true">
        + Ajouter une étape de versement
      </v-btn>
    </div>
    <div><InputsEditableText label="Commentaire:" compact /></div>
    <v-dialog
      v-model="dialogDeleteStepVersement"
      width="500"
    >
      <v-card>
        <v-card-title class="text-h5">
          Confirmer la suppression
        </v-card-title>

        <v-card-text>
          Vous êtes sur le point de supprimer une étape de versement. Cette action est irréversible.
        </v-card-text>

        <v-divider />

        <v-card-actions>
          <v-btn
            color="error"
            depressed
            @click="deleteStepConfirm"
          >
            Supprimer l'étape de versement
          </v-btn>
          <v-btn
            color="primary"
            outlined
            @click="dialogDeleteStepVersement = false"
          >
            Annuler
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
<script>
import { mdiMinusCircle, mdiCheckCircle, mdiCheck, mdiClose, mdiDotsVertical } from '@mdi/js'

export default
{
  name: 'VersStepPanel',
  props: {
    versementId: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      editedStepIndex: -1,
      editedStepItem: {
        id: '',
        name: '',
        isDone: false,
        category: '1',
        amount: 0,
        date: '',
        versement_id: ''
      },
      step: {
        id: '',
        name: '',
        isDone: false,
        category: '1',
        amount: 0,
        date: '',
        versement_id: ''
      },
      dialogDeleteStepVersement: false,
      showStepForm: false,
      icons: {
        mdiMinusCircle,
        mdiCheckCircle,
        mdiCheck,
        mdiClose,
        mdiDotsVertical
      },
      steps: [],
      headers: [
        {
          text: 'Étape des versements',
          align: 'start',
          sortable: false,
          value: 'name'
        },
        { text: 'Montant', value: 'amount' },
        { text: 'Versement effectué', value: 'isDone' },
        { text: 'Date', value: 'date' },
        { text: 'Catégorie', value: 'category' },
        { value: 'actions', align: 'end' }
      ]
    }
  },
  async mounted () {
    const { data: stepsData } = await this.$supabase.from('etapes_versement').select().eq('id', this.versementId)
    this.steps = stepsData
    console.log(' this.versementId: ', this.versementId)
    console.log('stepsData: ', stepsData)
  },
  methods: {
    deleteItem (item, index) {
      this.editedStepIndex = index
      this.editedStepItem = Object.assign({}, item)
      this.dialogDeleteStepVersement = true
    },
    async deleteStepConfirm () {
      console.log('Delete step versement')
      this.steps.splice(this.editedStepIndex, 1)
      this.dialogDeleteStepVersement = false
      console.log('this.editedStepItem: ', this.editedStepItem)
      await this.$supabase.from('etapes_versement').delete().eq('id', this.editedStepItem.id)
    },
    editLine (item, index) {
      const toEdit = this.steps.findIndex(index)
      toEdit.edit = true
    },
    async saveStep (step) {
      this.steps = [...this.steps, { ...step, edit: false }]
      this.showStepForm = false
      await this.$supabase.from('etapes_versement').insert({
        name: step.name,
        versement_id: this.versementId,
        isDone: step.is_done,
        category: step.category,
        amount: step.amount,
        date: '01/07/1992'// step.date
      }).select()
    }
  }
}
</script>
