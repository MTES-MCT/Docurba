<template>
  <div class="pt-7">
    <v-data-table
      v-if="versement.etapes_versement.length > 0"
      :headers="headers"
      :items="versement.etapes_versement"
      hide-default-footer
      :items-per-page="-1"
      class="elevation-0 mb-7"
    >
      <template #item="{item, index}">
        <tr v-if="editedStepIndex === index && editIsEdit">
          <td colspan="100%">
            <FriseDgdStepForm v-model="editedStepItem" class="mt-4" @save="saveStep(editedStepItem)" @cancel="editedStepIndex = -1; editIsEdit = false" />
          </td>
        </tr>
        <tr v-else>
          <td>{{ item.name }}</td>
          <td>{{ item.amount }}€</td>
          <td>{{ item.date }}</td>
          <td>{{ item.category }}</td>
          <td>
            <v-chip v-if="item.is_done" small label color="success-light" class="success--text font-weight-bold">
              <v-icon small color="success" class="mr-2">
                {{ icons.mdiMinusCircle }}
              </v-icon> OUI
            </v-chip>
            <span v-else> Non</span>
          </td>

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
        <FriseDgdStepForm @cancel="showStepForm = false" @save="saveStep" />
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
import { mdiMinusCircle, mdiCheckCircle, mdiDotsVertical } from '@mdi/js'

export default
{
  name: 'VersStepPanel',
  props: {
    versement: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      editedStepIndex: -1,
      editIsEdit: null,
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
        mdiDotsVertical
      },
      headers: [
        {
          text: 'Étape des versements',
          align: 'start',
          sortable: false,
          value: 'name'
        },
        { text: 'Montant', value: 'amount' },
        { text: 'Date', value: 'date' },
        { text: 'Catégorie', value: 'category' },
        { text: 'Versement effectué', value: 'isDone' },
        { value: 'actions', align: 'end' }
      ]
    }
  },
  methods: {
    saveStep (step) {
      this.$emit('save', { step, versement: this.versement })
      this.showStepForm = false
    },
    deleteItem (item, index) {
      this.editedStepIndex = index
      this.editedStepItem = Object.assign({}, item)
      this.dialogDeleteStepVersement = true
    },
    deleteStepConfirm () {
      this.$emit('delete', { ...this.editedStepItem })
      console.log('Delete step versement')
      this.dialogDeleteStepVersement = false
    },
    editLine (item, index) {
      this.editedStepIndex = index
      this.editIsEdit = true
      this.editedStepItem = { ...item }
    }
  }
}
</script>

<style scoped>
/* var(--v-primary-base) */
.v-data-table-header tr th span{
  color:red !important;
}
</style>
