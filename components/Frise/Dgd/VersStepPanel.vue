<template>
  <div>
    <v-divider />
    <v-data-table

      :headers="headers"
      :items="steps"
      hide-default-footer
      :items-per-page="-1"
      class="elevation-0"
    >
      <template #item="{item}">
        <tr v-if="item.edit">
          <td><v-text-field dense filled label="Étape prévue pour le versement" /></td>
          <td>lul</td>
        </tr>
        <tr v-else>
          <td>selected</td>
          <td>selected</td>
        </tr>
      </template>
    </v-data-table>
    <v-row v-if="showStepForm">
      <v-col cols="12" class="d-flex">
        <v-text-field v-model="name" min-width="200" dense filled placeholder="Étape prévue pour le versment" />
        <v-text-field v-model="amount" dense filled placeholder="Montant" />
        <v-text-field v-model="date" dense filled placeholder="Date" />
        <v-select v-model="category" :items="['1', '2', '3']" dense filled placeholder="Categorie" />
        <v-select v-model="isDone" :items="['oui','non']" dense filled placeholder="Effectué" />
        <div class="d-flex ml-2 ">
          <v-btn
            depressed
            color="primary"
            height="40"
            class="mr-2"
            @click="saveStep"
          >
            <v-icon>{{ icons.mdiCheck }}</v-icon>
          </v-btn>
          <v-btn
            color="primary"
            outlined
            depressed
            height="40"
            @click="showStepForm = false"
          >
            <v-icon>{{ icons.mdiClose }}</v-icon>
          </v-btn>
        </div>
      </v-col>
    </v-row>
    <div v-else>
      <v-btn class="mb-4" outlined color="primary" @click="showStepForm = true">
        + Ajouter une étape de versement
      </v-btn>
    </div>
    <div><InputsEditableText label="Commentaire:" compact /></div>
  </div>
</template>
<script>
import { mdiMinusCircle, mdiCheckCircle, mdiCheck, mdiClose } from '@mdi/js'

export default
{
  name: 'VersStepPanel',
  data () {
    return {
      showStepForm: false,
      icons: {
        mdiMinusCircle,
        mdiCheckCircle,
        mdiCheck,
        mdiClose
      },
      steps: [],
      headers: [
        {
          text: 'Étape des versements',
          align: 'start',
          sortable: false,
          value: 'name'
        },
        { text: 'Montant', value: 'calories' },
        { text: 'Versement effectué', value: 'fat' },
        { text: 'Date', value: 'carbs' },
        { text: 'Catégorie', value: 'protein' }
      ]
    }
  },
  methods: {
    saveStep () {
      this.steps = [...this.steps, {}]
    }
  }
}
